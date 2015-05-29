import ARM
from CairisHTTPError import ARMHTTPError, MalformedJSONHTTPError, MissingParameterHTTPError, SilentHTTPError
from data.CairisDAO import CairisDAO
from tools.JsonConverter import json_deserialize
from tools.PseudoClasses import ProjectSettings, Contributor, Revision
from tools.SessionValidator import check_required_keys

__author__ = 'Robin Quetin'


class ProjectDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)

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

    def from_json(self, request):
        json = request.get_json(silent=True)
        if json is False or json is None:
            self.close()
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        check_required_keys(json_dict, ProjectSettings.required)
        json_dict['__python_obj__'] = ProjectSettings.__module__+'.'+ProjectSettings.__name__

        contrs = json_dict['contributions'] or []
        if not isinstance(contrs, list):
            contrs = []

        for idx in range(0, len(contrs)):
            try:
                check_required_keys(contrs[idx], Contributor.required)
                json_dict['contributions'][idx] = (contrs[idx]['firstName'], contrs[idx]['surname'], contrs[idx]['affliation'], contrs[idx]['role'])
            except MissingParameterHTTPError:
                SilentHTTPError('A contribution did not contain all required fields. Skipping this one.')

        revisions = json_dict['revisions'] or []
        if not isinstance(revisions, list):
            revisions = []

        for idx in range(0, len(revisions)):
            try:
                check_required_keys(revisions[idx], Revision.required)
                json_dict['revisions'][idx] = (revisions[idx]['id'], revisions[idx]['date'], revisions[idx]['description'])
            except MissingParameterHTTPError:
                SilentHTTPError('A revision did not contain all required fields. Skipping this one.')

        json_dict['definitions'] = json_dict.get('definitions', None) or {}
        json_dict['definitions'] = json_dict['definitions'].items()

        settings = json_deserialize(json_dict)
        return settings