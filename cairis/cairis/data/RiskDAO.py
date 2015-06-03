import ARM
from CairisHTTPError import ARMHTTPError, ObjectNotFoundHTTPError, MalformedJSONHTTPError, MissingParameterHTTPError
from MisuseCase import MisuseCase
from MisuseCaseEnvironmentProperties import MisuseCaseEnvironmentProperties
from RiskParameters import RiskParameters
from data.CairisDAO import CairisDAO
from Risk import Risk
from alternative.EnvironmentModel import EnvironmentModel
from tools.JsonConverter import json_deserialize
from tools.ModelDefinitions import RiskModel, MisuseCaseModel, MisuseCaseEnvironmentPropertiesModel
from tools.PseudoClasses import RiskScore, RiskRating
from tools.SessionValidator import check_required_keys, get_fonts

__author__ = 'Robin Quetin'


class RiskDAO(CairisDAO):
    def __init__(self, session_id):
        CairisDAO.__init__(self, session_id)

    def get_risks(self, constraint_id=-1, simplify=True):
        try:
            risks = self.db_proxy.getRisks(constraintId=constraint_id)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

        if isinstance(risks, dict) and simplify:
            for key, value in risks.items():
                risks[key] = self.simplify(value)

        return risks

    def get_risk_names(self):
        risks = self.get_risks()
        risk_names = risks.keys()
        return risk_names

    def get_risk_by_name(self, name, simplify=True):
        """
        :rtype : Risk
        """
        risks = self.get_risks(simplify=simplify)
        found_risk = risks.get(name, None)

        if found_risk is None:
            raise ObjectNotFoundHTTPError(obj='The provided risk name')

        return found_risk

    def get_risk_analysis_model(self, environment_name, dim_name, obj_name):
        fontName, fontSize, apFontName = get_fonts(session_id=self.session_id)
        try:
            riskAnalysisModel = self.db_proxy.riskAnalysisModel(environment_name, dim_name, obj_name)
            tLinks = EnvironmentModel(riskAnalysisModel, environment_name, self.db_proxy, fontName=fontName, fontSize=fontSize)
            dot_code = tLinks.graph()
            if not dot_code:
                raise ObjectNotFoundHTTPError('The risk analysis model')
            return dot_code
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except Exception as ex:
            self.close()
            print(ex)

    def delete_risk(self, name):
        found_risk = self.get_risk_by_name(name)

        try:
            self.db_proxy.deleteRisk(found_risk.theId)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

    def add_risk(self, risk):
        params = RiskParameters(
            riskName=risk.theName,
            threatName=risk.theThreatName,
            vulName=risk.theVulnerabilityName,
            mc=risk.theMisuseCase,
            rTags=risk.theTags
        )

        try:
            risk_id = self.db_proxy.addRisk(params)
            return risk_id
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

    def update_risk(self, risk_name, risk):
        found_risk = self.get_risk_by_name(risk_name)
        found_mc = self.get_misuse_case_by_risk_name(risk_name)
        risk.theMisuseCase.theId = found_mc.theId

        params = RiskParameters(
            riskName=risk.theName,
            threatName=risk.theThreatName,
            vulName=risk.theVulnerabilityName,
            mc=risk.theMisuseCase,
            rTags=risk.theTags
        )
        params.setId(found_risk.theId)

        try:
            self.db_proxy.updateRisk(params)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

    # region Misuse cases
    def get_misuse_cases(self, constraint_id=-1, simplify=True):
        try:
            misuse_cases = self.db_proxy.getMisuseCases(constraintId=constraint_id)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

        if simplify:
            for key in misuse_cases:
                misuse_cases[key] = self.simplify(misuse_cases[key])

        return misuse_cases

    def get_misuse_case_by_risk_name(self, risk_name):
        found_risk = self.get_risk_by_name(risk_name)

        try:
            misuse_case = self.db_proxy.riskMisuseCase(found_risk.theId)
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

        if not misuse_case:
            self.close()
            raise ObjectNotFoundHTTPError('The misuse case associated with the risk')

        return misuse_case
    # endregion

    # region Risk scores
    def get_scores_by_rtve(self, risk_name, threat_name, vulnerability_name, environment_name):
        try:
            scores = self.db_proxy.riskScore(threat_name, vulnerability_name, environment_name, risk_name)
            if len(scores) > 0:
                scores = self.convert_scores(real_scores=scores)
            return scores
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)

    def convert_scores(self, real_scores=None, fake_scores=None):
        new_scores = []
        if real_scores:
            if len(real_scores) > 0:
                for idx in range(0, len(real_scores)):
                    real_score = real_scores[idx]
                    if len(real_score) == 4:
                        new_score = RiskScore(
                            response_name=real_score[0],
                            unmit_score=real_score[1],
                            mit_score=real_score[2],
                            details=real_score[3]
                        )
                        new_scores.append(new_score)
        elif fake_scores:
            if len(fake_scores) > 0:
                for idx in range(0, len(fake_scores)):
                    fake_score = fake_scores[idx]
                    assert isinstance(fake_score, RiskScore)
                    check_required_keys(fake_score, RiskScore.required)
                    if fake_score['unmitScore'] == -1:
                        fake_score['unmitScore'] = None
                    if fake_score['mitScore'] == -1:
                        fake_score['mitScore'] = None
                    new_score = (fake_score['responseName'], fake_score['unmitScore'], fake_score['mitScore'], fake_score['details'])
                    new_scores.append(new_score)
        else:
            self.close()
            raise MissingParameterHTTPError(param_names=['scores'])

        return new_scores
    # endregion

    # region Risk rating
    def get_risk_rating_by_tve(self, threat_name, vulnerability_name, environment_name):
        """
        :rtype: RiskRating
        """
        try:
            rating = self.db_proxy.riskRating(threat_name, vulnerability_name, environment_name)
            risk_rating = RiskRating(threat_name, vulnerability_name, environment_name, rating)
            return risk_rating
        except ARM.DatabaseProxyException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except ARM.ARMException as ex:
            self.close()
            raise ARMHTTPError(ex)
        except TypeError:
            self.close()
            raise ObjectNotFoundHTTPError(obj='A rating for the risk')
    # endregion

    def from_json(self, request):
        json = request.get_json(silent=True)
        if json is False or json is None:
            self.close()
            raise MalformedJSONHTTPError(data=request.get_data())

        json_dict = json['object']
        check_required_keys(json_dict, RiskModel.required)
        json_dict['__python_obj__'] = Risk.__module__+'.'+Risk.__name__

        if json_dict['theMisuseCase']:
            mc_dict = json_dict['theMisuseCase']
            check_required_keys(mc_dict, MisuseCaseModel.required)
            mc_dict['__python_obj__'] = MisuseCase.__module__+'.'+MisuseCase.__name__
            for idx in range(0, len(mc_dict['theEnvironmentProperties'])):
                mcep_dict = mc_dict['theEnvironmentProperties'][idx]
                check_required_keys(mcep_dict, MisuseCaseEnvironmentPropertiesModel.required)
                mcep_dict['__python_obj__'] = MisuseCaseEnvironmentProperties.__module__+'.'+MisuseCaseEnvironmentProperties.__name__
                mc_dict['theEnvironmentProperties'][idx] = mcep_dict
            json_dict['theMisuseCase'] = mc_dict

        risk = json_deserialize(json_dict)

        if isinstance(risk, Risk):
            return risk
        else:
            raise MalformedJSONHTTPError()

    def simplify(self, obj):
        """
        :type obj: Risk|MisuseCase
        """
        misuse_case = None
        if isinstance(obj, Risk):
            misuse_case = obj.theMisuseCase
        elif isinstance(obj, MisuseCase):
            misuse_case = obj

        misuse_case.theEnvironmentDictionary = {}
        delattr(misuse_case, 'theEnvironmentDictionary')

        if isinstance(obj, Risk):
            obj.theMisuseCase = misuse_case
        elif isinstance(obj, MisuseCase):
            obj = misuse_case

        return obj