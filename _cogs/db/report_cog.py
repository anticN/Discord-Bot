import discord
import pymongo
from discord.ext import commands
from discord import app_commands


# Connect to the MongoDB, change the connection string per your MongoDB environment
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["discBot"]
reports = db["reports"]


class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MAX_AMOUNT = 4

    def get_saved_reports(self, user_id, server_id):
        get_user = {"user_id": user_id, "server_id": server_id}
        if reports.find_one(get_user) is None:
            return 0
        else:
            user_reports = reports.find_one(get_user).get("amount_reports")
            return user_reports

    def get_all_server_reports(self, server_id):
        result = []
        for x in reports.find({"server_id": server_id}, {"_id": 0, "kicked": 0, "server_id": 0, "user_id": 0, "server": 0}).sort("amount_reports", -1):
            result.append(x)
        result_str = str(result)
        test = result_str.replace("user", "")
        test2 = test.replace("amount_reports", "")
        test3 = test2.replace("'", "")
        test4 = test3.replace("[", "")
        test5 = test4.replace("]", "")
        test6 = test5.replace("{", "")
        test7 = test6.replace("}", "\n")
        test8 = test7.replace(",", "")
        test9 = test8.replace(":", "")
        return test9

    def get_all_reports(self, server_id):
        # dev only
        pass

    def reset_server_reports(self, server_id):
        reports.delete_many({"server_id": server_id})

    def add_report(self, user, user_id, username, amount_from_report: int, server_id, server, current_reports):
        search = {
            "user_id": user_id,
            "server_id": server_id
        }
        new_report = {
            "server_id": server_id,
            "server": server,
            "user_id": user_id,
            "user": username,
            "amount_reports": amount_from_report,
            "kicked": False
        }
        if reports.count_documents(search) > 0:
            update_report = {"$set": {"amount_reports": current_reports}}
            reports.update_one(search, update_report)
            return f"{user.mention} has been reported and got {amount_from_report} reports. {self.MAX_AMOUNT - current_reports } more and you will be kicked/banned."
        else:
            reports.insert_one(new_report)
            return f"{user.mention} has been reported and got {amount_from_report} reports. {self.MAX_AMOUNT - amount_from_report } more and you will be kicked/banned."

    def check_if_doc_exists(self, user_id, server_id):
        search = {"user_id": user_id, "server_id": server_id}
        if reports.count_documents(search) > 0:
            return True
        else:
            return False

    def get_if_user_was_kicked(self, user_id, server_id):
        was_user_kicked = reports.find_one({"user_id": user_id, "server_id": server_id}).get("kicked")
        return was_user_kicked

    def reset_reports(self, user_id, server_id):
        reset = {"$set": {"amount_reports": 0}}
        reports.update_one({"user_id": user_id, "server_id": server_id}, reset)

    def update_if_user_was_kicked(self, user_id, server_id):
        update = {"$set": {"kicked": True}}
        reports.update_one({"user_id": user_id, "server_id": server_id}, update)

    def delete_reports(self, user_id, server_id, amount):
        del_amount = self.get_saved_reports(user_id, server_id) - amount
        delete = {"$set": {"amount_reports": del_amount}}
        reports.update_one({"user_id": user_id, "server_id": server_id}, delete)

    @app_commands.command(name="report", description="reports an user if he broke the server rules.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def new_reports(self, interaction: discord.Interaction, user: discord.User, amount: int):
        # reports an user if he broke the server rules. Checks the amount of reports and checks whether the user was already kicked or not.
        if not user.bot:
            if amount > 0:
                try:
                    if amount <= 4:
                        server = interaction.guild.name
                        server_id = interaction.guild.id
                        user_id = user.id
                        username = user.name
                        current_reports = self.get_saved_reports(user_id, server_id) + amount
                        if self.check_if_doc_exists(user_id, server_id) is True:
                            if current_reports >= 4:
                                self.reset_reports(user_id, server_id)
                                if self.get_if_user_was_kicked(user_id, server_id) is False:
                                    self.update_if_user_was_kicked(user_id, server_id)
                                    await interaction.guild.kick(user)
                                    await interaction.response.send_message(f"{username} got kicked from the server.")
                                    await user.send(f"You got kicked from the server {interaction.guild.name}")
                                    print(f"{user} has been reported and got {amount} report(s).")
                                    print(f"{username} got kicked from the server {interaction.guild.name}.")
                                elif self.get_if_user_was_kicked(user_id, server_id) is True:
                                    await interaction.guild.ban(user)
                                    await interaction.response.send_message(f"{user} was banned from the server")
                                    await user.send(f"You got banned from the server {interaction.guild.name}")
                                    print(f"{username} got banned from the server {interaction.guild.name}")
                            else:
                                await interaction.response.send_message(self.add_report(user, user_id, username, amount, server_id, server, current_reports))
                        else:
                            await interaction.response.send_message(self.add_report(user, user_id, username, amount, server_id, server, current_reports))
                    else:
                        await interaction.response.send_message(f"The maximal amount of reports is {self.MAX_AMOUNT}. And NO DECIMALS.")
                except Exception as e:
                    print(e)
                    await interaction.response.send_message(e)
            else:
                await interaction.response.send_message(f"No negative numbers allowed!! (1-4)")
        else:
            await interaction.response.send_message(f"You can't report a bot.")

    @app_commands.command(name="my-reports", description="shows the current amount of reports a user has")
    async def show_reports(self, interaction: discord.Interaction):
        # shows the current amount of reports a user has
        user_id = interaction.user.id
        server_id = interaction.guild.id
        if self.check_if_doc_exists(user_id, server_id) is True:
            await interaction.response.send_message(f"Your current amount of reports is: {self.get_saved_reports(user_id, server_id)}\n"
                                                    f"{self.MAX_AMOUNT - self.get_saved_reports(user_id, server_id)} more and you will be kicked/banned.")
        else:
            await interaction.response.send_message(f"You don't have any reports yet.")

    @app_commands.command(name="all-server-reports", description="shows all reports from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def show_all_reports(self, interaction: discord.Interaction):
        # shows all reports from the server
        server_id = interaction.guild.id
        if reports.count_documents({"server_id": server_id}) != 0:
            await interaction.response.send_message(f"All reports from {interaction.guild.name}:"
                                                    f"\n {self.get_all_server_reports(server_id)}")
        else:
            await interaction.response.send_message(f"Nobody in this server has any reports yet.")

    @app_commands.command(name="delete-report", description="deletes report(s) from an user (1-3)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def del_reports(self, interaction: discord.Interaction, user: discord.User, amount: int):
        # deletes report(s) from an user (1-3)
        if not user.bot:
            if amount > 0:
                user_id = user.id
                server_id = interaction.guild.id
                if self.check_if_doc_exists(user_id, server_id) is True:
                    if self.get_saved_reports(user_id, server_id) >= amount:
                        print(f"{amount} of {user}s reports got deleted")
                        self.delete_reports(user_id, server_id, amount)
                        await interaction.response.send_message(f"{user.mention}, {amount} of your report(s) got removed. Your current amount is: {self.get_saved_reports(user_id, server_id)}")
                    else:
                        await interaction.response.send_message(f"You can't delete {amount} reports, because the user only has {self.get_saved_reports(user_id, server_id)} reports.")
                else:
                    await interaction.response.send_message(f"{user.name} wasn't found or doesn't have any reports yet.")
            else:
                await interaction.response.send_message(f"No negative numbers allowed!! (1-4)")
        else:
            await interaction.response.send_message(f"You can't delete reports from a bot.")

    @app_commands.command(name="reset-reports", description="deletes all reports from a server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def reset_server(self, interaction: discord.Interaction):
        # deletes all reports from a server
        server_id = interaction.guild.id
        self.reset_server_reports(server_id)
        await interaction.response.send_message(f"All reports have been deleted.")