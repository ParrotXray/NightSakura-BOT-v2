from git import Repo
import os
from datetime import datetime

class GitControl():
    @classmethod
    async def git_push(self, path, url):
        repo_path = os.path.join(path)

        branch_name = datetime.now().strftime("%Y%m%d%H%M%S")

        repo = Repo.init(repo_path)

        repo.git.config("user.name", "")
        repo.git.config("user.email", "")

        repo.git.add('.')

        repo.index.commit(datetime.now().strftime("%Y%m%d%H%M%S"))

        new_branch = repo.create_head(branch_name)

        try:
            if 'origin' not in repo.remotes:
                origin = repo.create_remote('origin', url)
                origin.push(refspec=f'HEAD:{new_branch}')
            else:
                repo.remotes['origin'].push(refspec=f'HEAD:{new_branch}')
            
            print("DataBase has been backed up successfully.")
        except Exception as e:
            
            print(f"Requests are too frequent {e}.")






        