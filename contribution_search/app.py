import panel as pn
import os
from pathlib import Path
from contribution_search import CompanyOSSContributions


class App:
    """Class that creates an app UI for the CompanyOSSContributions class in contribution_search.py"""

    def __init__(self, env):
        """
        Inits the visible widgets as well as the loading symbol and a placeholder dataframe
        and puts them in a column layout.
        """
        self.env = env
        self.intro = pn.pane.HTML(
            """<h1>Company Open Source Contributions Search</h1>
        <p>This App takes a GitHub organization and returns a csv containing information about which open source repos its members contribute to.</p>
        <p>Enter the name of the GitHub organization you wish to search on below and press the "Search" button.</p>
        <p>It may take time to search on larger companies, so don't worry unless it's taking >10 minutes."""
        )
        self.warning = pn.pane.Markdown("")
        self.text = pn.widgets.TextInput(name="organization", placeholder="")
        self.search_button = pn.widgets.Button(name="Search", button_type="primary")
        self.search_button.on_click(self.searchOS)
        self.download_button = pn.widgets.Button(
            name="Download CSV of data", button_type="primary"
        )
        self.download_button.on_click(self.download)
        self.df = None
        self.show_df = pn.widgets.DataFrame(self.df)
        self.load = pn.extension(
            loading_spinner="dots", loading_color="#00aa41", sizing_mode="stretch_width"
        )
        self.layout = pn.Column(
            self.intro,
            self.warning,
            self.text,
            self.search_button,
            self.download_button,
            self.show_df,
        )

    def searchOS(
        self, event
    ):  # event parameter is there so it correctly links to a button press event
        """
        Takes the inputted org and a button press, runs the CompanyOSSContributions scraper on it and
        stores the data in a dataframe displayed on the app.
        """
        try:
            self.layout[1] = pn.pane.Markdown("")
            self.search_button.loading = True
            self.company_contributions = CompanyOSSContributions(self.text.value, self.env)
            self.df = self.company_contributions.get_all_repos()
            self.layout[-1] = pn.widgets.DataFrame(self.df)
            self.search_button.loading = False
        except Exception as e:
            self.layout[1] = pn.pane.Markdown("The requested company cannot be found.")
            self.search_button.loading = False
            print(e)
    def download(
        self, event
    ):  # event parameter is there so it correctly links to a button press event
        """
        Takes the current dataframe and a button press, downloads the currently displayed dataframe
        as a csv into the user's downloads folder.
        """
        try:

            self.company_contributions.download_csv()
            name = self.company_contributions.org + ".csv"
            path = os.path.join(Path.home(), "Downloads", name)
            self.layout[1] = pn.pane.Markdown(f"Download successful: {path}")
        except Exception as e:
            self.layout[1] = pn.pane.Markdown("Failed to download data.")
            print(e)

App('.github').layout.show()
