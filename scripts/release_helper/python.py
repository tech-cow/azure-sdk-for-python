from datetime import datetime
from collections import Counter
import re
from typing import Any, List, Dict, Set

from github.Repository import Repository

from common import IssueProcess, Common, get_origin_link_and_tag, IssuePackage
from utils import AUTO_CLOSE_LABEL, get_last_released_date, record_release, get_python_release_pipeline, run_pipeline

# assignee dict which will be assigned to handle issues
_PYTHON_OWNER = {'azure-sdk', 'msyyc'}
_PYTHON_ASSIGNEE = {'Wzb123456789'}

# labels
_CONFIGURED = 'Configured'
_AUTO_ASK_FOR_CHECK = 'auto-ask-check'
_BRANCH_ATTENTION = 'base-branch-attention'
_7_DAY_ATTENTION = '7days attention'
_MultiAPI = 'MultiAPI'
_ON_TIME = 'on time'
_HOLD_ON = 'HoldOn'
# record published issues
_FILE_OUT = 'published_issues_python.csv'


class IssueProcessPython(IssueProcess):

    def __init__(self, issue_package: IssuePackage, request_repo_dict: Dict[str, Repository],
                 assignee_candidates: Set[str], language_owner: Set[str]):
        IssueProcess.__init__(self, issue_package, request_repo_dict, assignee_candidates, language_owner)
        self.output_folder = ''
        self.pattern_resource_manager = re.compile(r'/specification/([\w-]+/)+resource-manager')
        self.delay_time = self.get_delay_time()
        self.python_tag = ''
        self.rest_repo_hash = ''

    def get_delay_time(self):
        q = [comment.updated_at
             for comment in self.issue_package.issue.get_comments() if comment.user.login not in self.language_owner]
        q.sort()
        return (datetime.now() - (self.created_time if not q else q[-1])).days

    @staticmethod
    def get_specefied_param(pattern: str, issue_body_list: List[str]) -> str:
        for line in issue_body_list:
            if pattern in line:
                return line.split(":", 1)[-1].strip()
        return ""

    def multi_api_policy(self) -> None:
        if (_MultiAPI in self.issue_package.labels_name) and (_AUTO_ASK_FOR_CHECK not in self.issue_package.labels_name):
            self.bot_advice.append(_MultiAPI)

    def get_edit_content(self) -> None:
        self.edit_content = f'\n{self.readme_link.replace("/readme.md", "")}\nReadme Tag: {self.target_readme_tag}'

    @property
    def is_multiapi(self):
        return _MultiAPI in self.issue_package.labels_name

    @property
    def readme_comparison(self) -> bool:
        # to see whether need change readme
        if _CONFIGURED in self.issue_package.labels_name:
            return False
        if 'package-' not in self.target_readme_tag:
            return True
        readme_path = self.pattern_resource_manager.search(self.readme_link).group() + '/readme.md'
        contents = str(self.issue_package.rest_repo.get_contents(readme_path).decoded_content)
        pattern_tag = re.compile(r'tag: package-[\w+-.]+')
        package_tags = pattern_tag.findall(contents)
        whether_same_tag = self.target_readme_tag in package_tags[0]
        whether_change_readme = not whether_same_tag or self.is_multiapi
        return whether_change_readme

    def auto_reply(self) -> None:
        if (_AUTO_ASK_FOR_CHECK not in self.issue_package.labels_name) or (_CONFIGURED in self.issue_package.labels_name):
            issue_number = self.issue_package.issue.number
            if not self.readme_comparison:
                try:
                    issue_link = self.issue_package.issue.html_url
                    release_pipeline_url = get_python_release_pipeline(self.output_folder)
                    res_run = run_pipeline(issue_link=issue_link,
                                           pipeline_url=release_pipeline_url,
                                           spec_readme=self.readme_link + '/readme.md',
                                           python_tag=self.python_tag,
                                           rest_repo_hash=self.rest_repo_hash
                                           )
                    if res_run:
                        self.log(f'{issue_number} run pipeline successfully')
                    else:
                        self.log(f'{issue_number} run pipeline fail')
                except Exception as e:
                    self.comment(f'hi @{self.assignee}, please check release-helper: `{e}`')
                if _AUTO_ASK_FOR_CHECK not in self.issue_package.labels_name:
                    self.add_label(_AUTO_ASK_FOR_CHECK)
            else:
                self.log(f'issue {issue_number} need config readme')

            if _CONFIGURED in self.issue_package.labels_name:
                self.issue_package.issue.remove_from_labels(_CONFIGURED)

    def attention_policy(self):
        if _BRANCH_ATTENTION in self.issue_package.labels_name:
            self.bot_advice.append('new version is 0.0.0, please check base branch!')

    def on_time_policy(self):
        if _ON_TIME in self.issue_package.labels_name:
            self.bot_advice.append('On time')

    def hold_on_policy(self):
        if _HOLD_ON in self.issue_package.labels_name:
            self.bot_advice.append('Hold on')

    def remind_policy(self):
        if self.delay_time >= 15 and _7_DAY_ATTENTION in self.issue_package.labels_name and self.date_from_target < 0:
            self.comment(
                f'hi @{self.owner}, the issue is closed since there is no reply for a long time. '
                'Please reopen it if necessary or create new one.')
            self.issue_package.issue.edit(state='close')
        elif self.delay_time >= 7 and _7_DAY_ATTENTION not in self.issue_package.labels_name and self.date_from_target < 7:
            self.comment(
                f'hi @{self.owner}, this release-request has been delayed more than 7 days,'
                ' please deal with it ASAP. We will close the issue if there is still no response after 7 days!')
            self.add_label(_7_DAY_ATTENTION)

    def auto_bot_advice(self):
        super().auto_bot_advice()
        self.multi_api_policy()
        self.attention_policy()
        self.on_time_policy()
        self.hold_on_policy()
        self.remind_policy()


    def auto_close(self) -> None:
        if AUTO_CLOSE_LABEL in self.issue_package.labels_name:
            return
        last_version, last_time = get_last_released_date(self.package_name)
        if last_time and last_time > self.created_time:
            comment = f'Hi @{self.owner}, pypi link: https://pypi.org/project/{self.package_name}/{last_version}/'
            self.issue_package.issue.create_comment(body=comment)
            self.issue_package.issue.edit(state='closed')
            self.add_label(AUTO_CLOSE_LABEL)
            self.is_open = False
            self.log(f"{self.issue_package.issue.number} has been closed!")
            record_release(self.package_name, self.issue_package.issue, _FILE_OUT, last_version)

    def auto_parse(self):
        super().auto_parse()
        issue_body_list = self.get_issue_body()
        self.readme_link = issue_body_list[0]
        if not re.findall(".+/Azure/azure-rest-api-specs/.+/resource-manager", self.readme_link):
            return

        # Get the specified tag and rest repo hash in issue body
        self.rest_repo_hash = self.get_specefied_param("->hash:", issue_body_list[:5])
        self.python_tag = self.get_specefied_param("->Readme Tag:", issue_body_list[:5])

        try:
            readme_python_path = self.pattern_resource_manager.search(self.readme_link).group() + '/readme.python.md'
            contents = str(self.issue_package.rest_repo.get_contents(readme_python_path).decoded_content)
        except Exception as e:
            raise Exception(f"fail to read readme.python.md: {e}")
        pattern_package = re.compile(r'package-name: [\w+-.]+')
        pattern_output = re.compile(r'\$\(python-sdks-folder\)/(.*?)/azure-')
        self.package_name = pattern_package.search(contents).group().split(':')[-1].strip()
        self.output_folder = pattern_output.search(contents).group().split('/')[1]
        if ('multi-api' in contents) and (_MultiAPI not in self.issue_package.labels_name):
            self.add_label(_MultiAPI)


    def run(self) -> None:
        super().run()
        self.auto_reply()
        self.auto_close()


class Python(Common):
    def __init__(self, issues, language_owner, sdk_assignees):
        super(Python, self).__init__(issues, language_owner, sdk_assignees)
        self.file_out_name = 'release_python_status.md'
        self.issue_process_function = IssueProcessPython

    def duplicated_policy(self):
        counter = Counter([item.package_name for item in self.result])
        for item in self.result:
            if counter[item.package_name] > 1:
                item.bot_advice.insert(0, 'duplicated issue  <br>')

    def run(self):
        self.proc_issue()
        self.duplicated_policy()
        self.output()


def python_process(issues: List[Any]):
    instance = Python(issues, _PYTHON_OWNER, _PYTHON_ASSIGNEE)
    instance.run()
