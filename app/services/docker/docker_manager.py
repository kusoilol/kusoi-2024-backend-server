import os
import tarfile

import docker

import docker.errors

from docker.models.containers import Container

from config import DOCKERPATH, TESTFOLDER, MAIN_TESTER

from app.schemas import Language


class DockerManager:
    client: docker.DockerClient
    container: Container | None | bytes

    def __init__(self) -> None:
        self.container = None
        self.client = docker.from_env()

    def build_image(self, path: str, tag: str = 'tester') -> None:
        if not os.path.isdir(path):
            raise docker.errors.NotFound("Path isn't a directory")
        if not os.path.isfile(os.path.join(path, 'Dockerfile')):
            raise docker.errors.NotFound("No Dockerfile located")
        for i in range(3):
            try:
                image, logs = self.client.images.build(path=path,
                                                       tag=tag)
                for lg in logs:
                    print(lg)
                break
            except docker.errors.DockerException:
                if i != 2:
                    continue
                raise

    def copy_file(self, src: str, dst: str, new_name: str | None = None):
        """
        https://stackoverflow.com/a/52716666
        """
        if self.container is None:
            raise docker.errors.NotFound("Container isn't running")
        os.chdir(os.path.dirname(src))
        src_name = os.path.basename(src)
        tar = tarfile.open(src + ".tar", mode='w')
        try:
            tar.add(src_name, arcname=(new_name if new_name else src_name))
        finally:
            tar.close()
        data = open(src + ".tar", 'rb').read()
        os.remove(src + ".tar")
        self.container.put_archive(os.path.dirname(dst), data)

    def run_container(self, tag: str = 'tester', detach: bool = True) -> None | str:
        for i in range(3):
            try:
                self.container = self.client.containers.run(
                    image=tag, detach=detach, remove=(not detach), tty=detach,
                    network_disabled=True)
                if not detach:
                    return self.container.decode()
                break
            except docker.errors.DockerException:
                if i != 2:
                    continue
                self.client.containers.prune()
                raise

    def run_cmd(self, cmd: list[str] | str) -> str | None:
        try:
            if not self.container or isinstance(self.container, bytes):
                return None
            exit_code, output = self.container.exec_run(cmd=cmd)
            return output.decode()
        except docker.errors.DockerException:
            self.cleanup()
            raise

    def restrict_permission(self, user: str, filepath: str):
        if not self.container or isinstance(self.container, bytes):
            return False
        self.run_cmd(["chown", user, filepath])
        self.run_cmd(["chmod", "700", filepath])
        return True

    def cleanup(self) -> None:
        try:
            if self.container and not isinstance(self.container, bytes):
                self.container.remove(force=True)
            self.client.close()
        except docker.errors.DockerException:
            pass

    def setup_player(self, path: str, language: Language, username: str):
        filename = username + language.value
        self.copy_file(path, TESTFOLDER, filename)
        self.restrict_permission(username, filename)

    def run_game(self, alice_path: str, alice_lang: Language,
                 bob_path: str, bob_lang: Language) -> str:
        try:
            self.build_image(DOCKERPATH)
            self.run_container()
            self.setup_player(alice_path, alice_lang, 'alice')
            self.setup_player(bob_path, bob_lang, 'bob')
            res = self.run_cmd(["python", MAIN_TESTER])
            return res
        finally:
            self.cleanup()


PATH_1 = "C:\\Programming\\KUSOI\\server\\app\\services\\docker\\test\\alice.py"
PATH_2 = "C:\\Programming\\KUSOI\\server\\app\\services\\docker\\test\\bob.py"
# DST_1 = "app/"
# DST_2 = "app/"
# DDST_1 = "alice.py"
# DDST_2 = "bob.py"
#
# dm = DockerManager()
# dm.build_image("C:\\Programming\\KUSOI\\server\\app\\services\\docker\\dockerhome")
# dm.run_container()
# dm.copy_file(PATH_1, DST_1)
# dm.copy_file(PATH_2, DST_2)
# print(dm.run_cmd("pwd"))
# print(dm.run_cmd("ls -R"))
# print(dm.run_cmd(["chown", "player1", DDST_1]))
# print(dm.run_cmd(["chown", "player2", DDST_2]))
# print(dm.restrict_permission("player1", DDST_1))
# print(dm.restrict_permission("player2", DDST_2))
# print(dm.run_cmd("ls -R -l"))
# print(dm.run_cmd(["python", TESTER]))
# dm.cleanup()

# dm = DockerManager()
# result = dm.run_game(PATH_1, Language.PYTHON, PATH_2, Language.PYTHON)
# print(result)
