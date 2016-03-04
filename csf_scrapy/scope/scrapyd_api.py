import requests
import json


def resp(func):
    def __call_func(*args, **kwargs):
        resp = func(*args, **kwargs)
        if not resp.ok:
            return {"status": "error", "message": ""}
        return json.loads(resp.content)
    return __call_func


class ScrapydApi:
    def __init__(self, url):
        self.__url = url + "/%s"

    @resp
    def schedule(self, project, spider, **kwargs):
        kwargs["project"] = project
        kwargs["spider"] = spider
        return requests.post(self.__url % "schedule.json", kwargs)

    @resp
    def cancel(self, project, job):
        return requests.post(self.__url % "cancel.json", {"project": project, "job": job})

    @resp
    def list_projects(self):
        return requests.get(self.__url % "listprojects.json")

    @resp
    def list_versions(self, project):
        return requests.get(self.__url % "listversions.json", {"project": project})

    @resp
    def list_spiders(self, project, _version=None):
        kwargs = {"project": project}
        if _version:
            kwargs["_version"] = _version
        return requests.get(self.__url % "listspiders.json", kwargs)

    @resp
    def list_jobs(self, project):
        return requests.get(self.__url % "listjobs.json", {"project": project})

    @resp
    def del_version(self, project, version):
        return requests.post(self.__url % "delversion.json", {"project": project, "version": version})

    @resp
    def del_project(self, project):
        return requests.post(self.__url % "delproject.json", {"project": project})


if __name__ == "__main__":
    sa=ScrapydApi("http://127.0.0.1:6801")
    print sa.list_jobs("scope")
