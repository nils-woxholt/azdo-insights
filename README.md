# Get insights into your contributions to a project in Azure Devops

When looking back on a project, it's often interesting to reflect on your contributions to that project.

In Azure DevOps, you can click around the UI but often finding answers to deeper questions requires a lot of digging into deeper screens to extract insights.

This is a small tool written in Python that helps to surface some insights by leveraging the Azure DevOps REST api.

## Features

For a specified repo and person, create a markdown output file showing:  

- Summary counts of:
  - Pull requests (PR's)
  - PR's that I reviewed
  - All of my comments on PR's
- List of all my PR's
- List of all PR's that I reviewed
- List of all my comments

## Getting Started

1. Clone the repo
1. Create a python virtual environment

    ```bash
    cd src
    python -m venv .venv
    ```

1. Install the python library dependencies

    ```bash
    pip install -r requirements.txt
    ```

1. Create a file called `.env` by copying the `.env.sample` file. (You can also set these as environment variables)
1. Capture the settings for your Azure DevOps repo in each of the values in the file
1. Run the program (make sure you're in the `src` folder)

    ```bash
    # pass the name at runtime 
    # use the display name in Azure Devops
    # (the program will ask for it if you don't)
    python main.py --name 'Fred Flintstone'
    ```

## Options

```bash
python main.py --help               
Usage: main.py [OPTIONS]

Options:
  --name TEXT                The display name in Azure DevOps
  --fetch INTEGER            How many rows to fetch
  --comment-trim INTEGER     Ignore comments shorter than this length
  --include-replies BOOLEAN  Include my comments that are replies to other comments
  --help                     Show this message and exit.
```
