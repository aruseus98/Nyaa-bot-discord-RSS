import discord
import asyncio
import logging
import re
from datetime import datetime
from config.config import DISCORD_CHANNEL_ID
from utils.functions import get_rss_feed, read_last_entry, write_last_entry, scrape_file_name_and_title, normalize_title, read_rss_urls_from_json
from state.state_manager import get_group_state, update_group_state

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_run = True
        self.feed_urls = []

    async def on_ready(self):
        logging.info(f'Logged in as {self.user}')
        print(f'We have logged in as {self.user}')

        self.channel_to_notify = self.get_channel(DISCORD_CHANNEL_ID)
        if self.channel_to_notify is None:
            logging.error(f"Channel with ID {DISCORD_CHANNEL_ID} not found")
        else:
            self.check_rss_task = self.loop.create_task(self.check_rss_feeds())

    async def check_rss_feeds(self):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                logging.info("Reading RSS feed URLs from JSON file")
                self.feed_urls = read_rss_urls_from_json('urls/rss_urls.json')
                logging.info(f"Read URLs: {self.feed_urls}")
            except Exception as e:
                logging.error(f"Error while reading RSS URLs from JSON: {e}")

            for feed_url in self.feed_urls:
                logging.info(f"Checking RSS feed: {feed_url}")
                feed_entries = get_rss_feed(feed_url)

                if feed_entries:
                    entries_to_check = feed_entries[:4]
                    last_entry_titles = await read_last_entry(feed_url)
                    logging.debug(f"Last entries from file for {feed_url}: {last_entry_titles}")

                    last_entry_titles_set = set(last_entry_titles)
                    logging.debug(f"Last entry titles extracted for {feed_url}: {last_entry_titles_set}")

                    new_entry_titles = []

                    grouped_entries = {}
                    for entry in entries_to_check:
                        normalized_title = normalize_title(entry.title)
                        logging.debug(f"Original title: {entry.title}, Normalized title: {normalized_title}")
                        if normalized_title not in grouped_entries:
                            grouped_entries[normalized_title] = []
                        grouped_entries[normalized_title].append(entry)

                    for group_title, entries in grouped_entries.items():
                        logging.debug(f"Processing group: {group_title} with {len(entries)} entries")
                        description = ""
                        file_size = None
                        episode_title = None
                        audio_languages = None
                        group_has_new_entries = False

                        group_sent = get_group_state(feed_url, group_title)
                        logging.debug(f"Group state for {group_title}: {group_sent}")
                        if not group_sent:
                            for entry in entries:
                                entry_url = entry.id.strip()
                                entry_id = entry_url.split('/')[-1]
                                logging.debug(f"Checking entry: {entry_url} with ID: {entry_id}")

                                if entry_id not in last_entry_titles_set:  # Vérifier l'identifiant unique au lieu du titre
                                    logging.debug(f"New entry detected: {entry_url}")
                                    new_entry_titles.append(entry_id)
                                    group_has_new_entries = True

                                    last_entry_titles_set.add(entry_id)

                                    file_name, episode_title, audio_languages = scrape_file_name_and_title(entry.link)
                                    logging.debug(f"Scraped file name: {file_name}, episode title: {episode_title}, audio languages: {audio_languages}")
                                    if file_name:
                                        match = re.search(r'(\d+(\.\d+)?\s*(MiB|GiB))', file_name)
                                        file_size = match.group(1) if match else None
                                        file_name_clean = re.sub(r'\s*\(\d+(\.\d+)?\s*(MiB|GiB)\)', '', file_name)
                                        description += f"[{file_name_clean}]({entry.link})\n"

                            logging.debug(f"Group has new entries: {group_has_new_entries} for group: {group_title}")
                            if group_has_new_entries and description:
                                logging.debug(f"group_has_new_entries: {group_has_new_entries}")
                                logging.debug(f"description: {description}")
                                logging.debug(f"Sending embed for group: {group_title}")
                                current_time = datetime.now().strftime('%I:%M %p')
                                thumbnail_url = ""
                                if "PLACEHOLDER_1" in entries[0].title:
                                    thumbnail_url = "https://i.imgur.com/ID1.png"
                                elif "PLACEHOLDER_2" in entries[0].title:
                                    thumbnail_url = "https://i.imgur.com/ID2.png"
                                elif "PLACEHOLDER_3" in entries[0].title:
                                    thumbnail_url = "https://i.imgur.com/ID3.png"
                                elif "PLACEHOLDER_4" in entries[0].title:
                                    thumbnail_url = "https://i.imgur.com/ID4.png"
                                else:
                                    thumbnail_url = "https://i.imgur.com/ID5.png"

                                icon_url = "https://i.imgur.com/mTZbKXz.png"
                                embed = discord.Embed(description="", color=0x222222)
                                embed.set_author(name=group_title, icon_url=icon_url)
                                if thumbnail_url:
                                    embed.set_thumbnail(url=thumbnail_url)

                                embed.add_field(name=":page_facing_up: Titre", value=episode_title if episode_title else group_title, inline=False)
                                embed.add_field(name=":speaker: Audios", value=audio_languages if audio_languages else "Unknown", inline=False)
                                embed.add_field(name=":link: Lien de téléchargement", value=description.strip(), inline=False)
                                embed.set_image(url="https://i.imgur.com/ID6.png")

                                if file_size:
                                    embed.set_footer(text=f"Today at {current_time}")

                                await self.channel_to_notify.send(embed=embed)
                                logging.debug(f"Embed sent for group: {group_title} with entries: {new_entry_titles}")

                                update_group_state(feed_url, group_title, True)

                    if new_entry_titles:
                        logging.debug(f"New entries to add for {feed_url}: {new_entry_titles}")
                        last_entry_titles.extend(new_entry_titles)
                        last_entry_titles = last_entry_titles[-4:]
                        await write_last_entry(feed_url, last_entry_titles)
                        logging.info(f"Wrote last entry titles for {feed_url}: {last_entry_titles}")

                else:
                    logging.info(f"No new entries to send for {feed_url}.")

            await asyncio.sleep(120)
