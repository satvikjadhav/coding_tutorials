# Get Good at Git

## Git Core Concepts

## Git Techniques and Shortcuts (Advanced)

**Commit and add all the untracked files in one line**
```git
git commit -am 'that was easy'
```
This automatically adds `git add .` 

**Creating custom commands in git**
```git
git config --global alias.ac 'commit -am'
```
The line above will create a `git` command `ac`, that will run `commit -am`
Useful aliases:
- `alias.uncommit="git reset HEAD~1"`
- `alias.recommit="git commit --amend --no-edit"`
- `alias.editcommit="git commit --amend"`
- `These.are my all time favorite aliases`

**Resetting/Changing the message of the last commit**
```git
git commit --amend -m 'noice!'
```
The line above will simply update the latest commit. 
And also if we want to update the last commit with new files we can use `git add .` and then  `git commit --amend --no-edit` to update the last commit without change the messages
However, this will only work if we have not pushed our code to a remote repo

**Force pushing updates**
```git
git push origin main --force-with-lease
```
The line above will push avoid pushing the code if it would overwrite something we didn't anticipate (coworker's code)

**Reverting changes**
```git
git revert <commit-hash>
```
The line above lets us take one commit and go back to the state that was there previously. 
This is kind of like an undo, but it doesn't remove the original commit from the history

**Stash**
```git
git stash
```
Useful when we are working on some changes that "almost" work and can't be committed yet as they break everything else. 
`git stash` will remove the changes from our current directory and save them for later use without committing them to the repo

To add the changes back into our code we can use the following command:
```git
git stash pop
```

However, what if we use it a lot and want to save number of different changes?
For that we can use the following line
```git
git stash save <save_name>
```
And use the `<save_name>` later to reference a specific `stash` using the following commands
```git
git stash list
git stash apply <respective_index_value>
```

**Viewing the history of our commits**
The problem with `git log` is that it becomes harder and harder to read as our project grows
To make the output more readable and easier to follow, we can use the following command: 
```git
git log --graph --online --decorate
```

**Squashing our commits**
Imagine we are working on a different branch that as 3 different commits, and we are now ready to merge it into a master branch.
But all those commit messages are kind of pointless and one commit message would probably be better.
We can do it by using the following commands: 
```git
git rebase main --interactive
```
This will pull up a file with list of commits on the main branch
In this we use `pick` when we want to use that specific commit. 
To change the commit message we can use the `reword` command
And if we want to squash or meld the previous commits into one commit we use the `squash` command

**Destroy Things**
Lets imagine we have a remote repo and a local repo that we have been making changes to, but things haven't been going too well. And now we want to go back to the original state as the remote repo. 
To do that, we would execute the following commands
```git
git fetch origin
```
To get the latest code in our remote repo
```git
git reset --hard origin
```
Override our local code with the remote code, but be careful as doing this means our local changes will be lost forever
Even after all this we might still be left with some random files that are untracked. To fix this, we run the following command: 
```git
git clean -df
```
