import ARM
from CairisHTTPError import ARMHTTPError
from data.CairisDAO import CairisDAO
from tools.PseudoClasses import ProjectSettings

__author__ = 'Robin Quetin'


class ProjectDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(session_id)

    def create_new_project(self):
        try:
            self.db_proxy.clearDatabase(session_id=self.session_id)
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

    def get_settings(self):
        try:
            pSettings = self.db_proxy.getProjectSettings()
            pDict = self.db_proxy.getDictionary()
            contributors = self.db_proxy.getContributors()
            revisions = self.db_proxy.getRevisions()
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)

        settings = ProjectSettings(pSettings, pDict, contributors, revisions)
        return settings

    def apply_settings(self, settings):
        assert isinstance(settings, ProjectSettings)
        try:
            self.db_proxy.updateSettings(
                settings.projectName,
                settings.projectBackground,
                settings.projectGoals,
                settings.projectScope,
                settings.definitions,
                settings.contributions,
                settings.revisions,
                settings.richPicture,
                settings.fontSize,
                settings.fontName
            )
        except ARM.DatabaseProxyException as ex:
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            raise ARMHTTPError(ex)