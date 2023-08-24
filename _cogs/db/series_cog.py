import pymongo
import json
from discord.ext import commands

# Connect to the MongoDB, change the connection string per your MongoDB environment
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["discBot"]
collection = db["series"]
#TODO §mys mit json lösen anstatt 9x .replace

class SeriesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def new_series(self, user_id, user, series, episode_chapter: int):
        new_insert = {
            "user_id": user_id,
            "name": user,
            "series": series,
            "episode": episode_chapter
        }
        collection.insert_one(new_insert)
        print(f"{user} saved {series} (ep {episode_chapter})")
        return f"{series} has been added"

    def list_to_string(self, s):
        str1 = " "

        return str1.join(s)

    def show_all_from_user(self, user_id):
        result = []
        for x in collection.find({"user_id": user_id}, {"_id": 0, "name": 0, "user_id": 0}).sort("episode", -1):
            result.append(x)
        #self.list_to_string(result)
        #test = "\n".join(i["series"] for i in result)
        #test2 = "\n".join(j["episode"] for j in result)
        #test3 = test + test2
        result_str = str(result)
        test = result_str.replace("series", "")
        test2 = test.replace("episode", "")
        test3 = test2.replace("'", "")
        test4 = test3.replace("[", "")
        test5 = test4.replace("]", "")
        test6 = test5.replace("{", "")
        test7 = test6.replace("}", "\n")
        test8 = test7.replace(",", "")
        test9 = test8.replace(":", "")
        #test10 = test9.replace(" ", "", 1)
        return test9

    def update(self, user_id, series, new_episode):
        query = {
            "user_id": user_id,
            "series": series
        }
        new_ep = {"$set": {"episode": new_episode}}

        collection.update_one(query, new_ep)
        return f"{series} has been updated to episode/chapter {new_episode}"

    def delete(self, user_id, series):
        query = {
            "user_id": user_id,
            "series": series
        }

        collection.delete_one(query)
        return f"{series} has been deleted"

    def check_series(self, user_id, series):
        if collection.count_documents({"user_id": user_id, "series": series}) > 0:
            return True
        elif collection.count_documents({"user_id": user_id, "series": series}) == 0:
            return False

    def get_episode(self, user_id):
        series = "tbate"
        if self.check_series(user_id, series) is True:
            ep = collection.find_one({"user_id": user_id, "series": series}).get("episode")
            return ep

    @commands.command(pass_context=True, name="newSeries", aliases=["ns"], help="Adds a new series to the user")
    async def new_save(self, ctx, series: str, episode: int):
        # saves a new series to the user
        member = ctx.message.author.name
        member_id = ctx.message.author.id
        if self.check_series(member_id, series) is False:
            await ctx.send(self.new_series(member_id, member, series, episode))
        else:
            await ctx.send(f"{series} already exists.")

    @commands.command(pass_context=True, name="showSeries", aliases=["myS", "mys"], help="shows all the saved series from a user")
    async def show_all(self, ctx):
        # shows all the saved series from a user
        member = ctx.message.author.name
        member_id = ctx.message.author.id
        if collection.count_documents({"user_id": member_id}) != 0:
            await ctx.send(f"Your saved series:\n {self.show_all_from_user(member_id)}")
        else:
            await ctx.send("You don't have any saved series.")

    @commands.command(pass_context=True, name="updateSeries", aliases=["us"], help="updates a series from a user")
    async def update_series(self, ctx, series: str, new_episode: int):
        # updates a series from a user
        member = ctx.message.author.name
        member_id = ctx.message.author.id
        if self.check_series(member_id, series) is True:
            await ctx.send(self.update(member_id, series, new_episode))
            print(f"{member} updated {series} to {new_episode}")
        else:
            await ctx.send(f"{series} wasn't found. Try with a different spelling.")

    @commands.command(pass_context=True, name="deleteSeries", aliases=["ds"], help="deletes a series from a user")
    async def delete_series(self, ctx, series: str):
        # deletes a series from a user
        member = ctx.message.author.name
        member_id = ctx.message.author.id
        if self.check_series(member_id, series) is True:
            await ctx.send(self.delete(member_id, series))
            print(f"{member} deleted {series}")
        else:
            await ctx.send(f"{series} wasn't found. Try with a different spelling.")

    @commands.command(pass_context=True, name="tbate", help="sends link with users current chapter")
    async def send_link(self, ctx):
        # sends the users link to his tbate chapter
        member_id = ctx.message.author.id
        if self.check_series(member_id, "tbate") is True:
            await ctx.send(f"Your link to your current chapter:"
                            f"\nhttps://isekaiscan.com/manga/the-beginning-after-the-end/chapter-{self.get_episode(member_id)}/")
        else:
            await ctx.send(f"You haven't saved 'tbate' yet")