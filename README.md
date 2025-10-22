[![Run App Bader, Cole](https://github.com/Husker-Bader/GithubActions/actions/workflows/ci.yml/badge.svg)](https://github.com/Husker-Bader/GithubActions/actions/workflows/ci.yml)

# Do not submit a pull request to `kgerot/GithubActions` or `dteske/TraviCI`. Not following this instruction can ruin the lab for others, so pay attention.

I receive around 60 pull requests every semester and have to manually delete each request and action run. Your actions will automatically fail if you open a pull request

# Github Actions Lab

Because Travis CI is no longer free, we are going to look at how Github Actions can provide continuous integration on a sample project.

Continuous integration can be used to perfom checks on written code, making sure that unit tests always pass or that formatting is followed, and that when changes are made, they don't break other areas of the code.

Fork and clone the repo to your computer to get started.

## Run the Console App
Just as a sanity check, make sure that everything is working before you begin. Try out the console app, see if you can break it and where the weaknesses in the code are. Try manually running the tests.

## Set up Github Actions to build the Console App

First, let's explore the Action UI on Github. Go to the Actions Tab and look at any running jobs.
Currently, there should be one job that has run successfully. 

![Actions Tab](./assets/imgs/actions-tab.PNG)

If you open that job, you'll see we've programmed the action to just echo `Hello, World!`. If yo ucannot find a job, that's okay. Sometimes Github will not run an  action immediately upon forking.

We want our action to build our project. To do this, navigate to the file `.github/workflows/run-app.yaml`.
This is where we have define a workflow that runs a process called `Basic Action` that echos `Hello, World!`. It runs on the latest Ubuntu OS and runs everytime you push.

Replace the contents of the file with the code below

```yaml
name: 'Run App <last name>, <first name>'

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: install dotnet
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.x'
      - name: build
        run: dotnet build
      - name: run unit tests
        run: dotnet test
```

- Replace FullName on the first line with your name for grading.
- Commit and push these changes to master
- Open the Actions and see if your build is running (should be under the name of your commit). 

## Build Status Badge

Right now the build status badge at the top of this Readme is for the repo `kgerot/GithubActions` and  we want it to be *your* repository. 

To change this, go to your last build in Actions and open it. Click the three dots on the right side of the screen and click Create status badge.

Here, you can copy the markdown and replace the badge at the top of this Readme on the Github website or in VS.

![Inside Job](./assets/imgs/inner-test.PNG)

![Badge Markdown](./assets/imgs/badge-markdown.PNG)

## Implement the Power method
Once Github Actions is up and running, it should rebuild every time you push a change, or open a pull request. Let's test this out.

- Implement the `Power` method found in `Program.cs`.
- Commit and push the change to a different branch.
- Open a pull request **to your repository's main branch** 

### Do not submit a pull request to `kgerot/GithubActions` or `dteske/TraviCI`. Not following this instruction can ruin the lab for others. 

If you accidentally submit a pull request to the master branch of `kgerot/GithubActions`, please invite kgerot as a reviewer on the request so I can close it and properly fix the repository.

## Set up Github Actions to run Unit Tests
To run the tests after every change, we'll have to modify the .yaml slightly. Add the follwing code to the steps section:

```yaml
      - name: run unit tests
        run: dotnet test
```

Your .yaml file should look like this now:
```yaml
name: 'Run App <last name>, <first name>'

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: install dotnet
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.x'
      - name: build
        run: dotnet build
      - name: run unit tests
        run: dotnet test
```

This is the MSTest test runner, and will allow GithubActions to run the tests on the server from the command line.
Commit and push this change to main.

Open Actions and make sure the build completes.

If you've done this correctly, the following should appear at the bottom of your build log:

![nunit-tests](./assets/imgs/passing-unit-tests.PNG)

(once you have finished, use the same output to show all your unit tests)

## Implement the other unit tests
Follow the same format as the addition unit tests, and implement tests for the rest of the operations defined in `Program.cs`.

- Run the tests locally, and intentionally make one fail.
- Commit and push the changes to a different branch.
- Open a new pull request **to your own main branch, not `kgerot/GithubActions` or `dteske25/TravisCI`**.

Github Actions will detect the pull request, and build it. Since we have a test failing, it should detect that. A failed build will look like the following;

![failed build](./assets/imgs/failed-job.PNG)

And in GitHub it will look like:

![pr overview failed](./assets/imgs/failed-pull.PNG)

- Push a change on the same branch to fix the test.
- See if the build completes successfully.

In GitHub, that will look like the following:

![pr overview passed](./assets/imgs/passed-pull.PNG)

If everything passes, feel free to merge. You are now using CI.
