import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import dotenv_values


class CompanyOSSContributions:
    """
    A class that takes a GitHub organization and returns a csv containing
    information about which open source repos its members contribute to.
    """
    def __init__(self, company, env):
        """
        Takes GitHub tokens from the environment and makes auth headers.
        """
        config = dotenv_values(env)
        self.access_token = config["access_token"]
        self.org = company
        self.headers = {"Authorization": f"token {self.access_token}"}

    def get_members(self):
        """
        Calls the api once to get a list of members of the company org.
        """
        people_response = requests.get(
            headers=self.headers,
            url=f"https://api.github.com/orgs/{self.org}/members?per_page=100",
        )
        self.people_json = people_response.json()
        self.names = []
        for person in self.people_json:
            self.names.append(person["login"])
        return self.names

    def list_open_source_repos(self, user):
        """
        Iterates through a user's repos and records the number of contributions made by the user
        if the repo is open source and forked.
        Args: Takes one username
        Returns: Three lists of the same length that can be appended to the final dataframe
            - A list of just the username, so the dataframe has a column indicating which user contributed
            - A list of open source repos that the user forked and contributed to
            - A list of how many contributions the user made to each repo
        """

        df = pd.read_csv(
            "all_licenses_updated.csv"
        )  # csv containing a list of open source licenses to check the repo license against
        response = requests.get(
            headers=self.headers,
            url=f"https://api.github.com/users/{user}/repos?per_page=100",
        )
        repos = response.json()
        # using pagination to iterate through every page of a user's repos using the 'next' url in the response headers:
        while "next" in response.links.keys():
            response = requests.get(
                headers=self.headers, url=response.links["next"]["url"]
            )
            repos.extend(response.json())
        open_source = []
        names = []
        contributions = []
        for repo in repos:
            if repo["license"] == None:
                pass
            elif repo["license"]["name"] not in df["license_name"].to_list():
                pass
            elif repo["fork"] == False:
                pass
            else:
                url = repo["contributors_url"] + "?per_page=100&page=1"
                response = requests.get(
                    headers=self.headers, url=url + "?per_page=100&page=1"
                )
                contributors = response.json()
                cont = 0
                if bool(contributors) == True:
                    for contributor in contributors:
                        if contributor["login"] == user:
                            cont = contributor["contributions"]
                            break
                        else:
                            cont = 0
                    while cont == 0 and "next" in response.links.keys():
                        for contributor in contributors:
                            if contributor["login"] == user:
                                cont = contributor["contributions"]
                                break
                            else:
                                cont = 0
                        response = requests.get(
                            headers=self.headers, url=response.links["next"]["url"]
                        )
                        contributors = response.json()
                        for contributor in contributors:
                            if contributor["login"] == user:
                                cont = contributor["contributions"]
                                break
                            else:
                                cont = 0
                if cont != 0:
                    names.append(user)
                    contributions.append(cont)
                    open_source.append(repo["name"])
                else:
                    pass
        return names, open_source, contributions

    def get_all_repos(self):
        """
        Runs all of the above for one company.
        """
        members = self.get_members()
        self.data = {}
        all_names = []
        all_repos = []
        all_contributions = []
        for member in members:
            names, open_source, contributions = self.list_open_source_repos(member)

            all_names.extend(names)
            all_repos.extend(open_source)
            all_contributions.extend(contributions)

        self.data["person"] = all_names
        self.data["open_source_repos"] = all_repos
        self.data["contribution_to_repo"] = all_contributions
        print(self.data)
        self.df = pd.DataFrame(self.data)
        return self.df

    def download_csv(self, name=None):
        """
        Stores the data in a csv named after the company in question.
        """
        if name is None:
            name = self.org + ".csv"
        self.df.to_csv(os.path.join(Path.home(), "Downloads", name))

'''
test = CompanyOSSContributions("QuickenLoans", ".github")
test.get_all_repos()
test.download_csv()
'''

