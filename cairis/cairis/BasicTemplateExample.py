import os

__author__ = 'Raf'
from mako.lookup import TemplateLookup
from BaseTemplates.NavObject import NavObject
import webbrowser


file = NavObject("#", "File")
file.setIcon("fa fa-file-o")
levellist = list()
levellist.append(NavObject("#", "File"))
levellist.append(NavObject("#", "Open"))
levellist.append(NavObject('#', "Save"))
levellist.append(NavObject('#', "Export"))
levellist.append(NavObject('#', "Documentation"))
file.setmultilevel(levellist)

req = NavObject("#", "Requirement Management")
req.setIcon("fa fa-adjust")
levellist = list()
levellist.append(NavObject("#", "Commit"))
levellist.append(NavObject("#", "Add"))
levellist.append(NavObject('#', "Delete"))
levellist.append(NavObject('#', "Domain Properties"))
levellist.append(NavObject('#', "Goals"))
levellist.append(NavObject('#', "Obstacles"))
req.setmultilevel(levellist)

risk = NavObject("#", "Risk Management")
risk.setIcon("fa fa-exclamation")
levellist = list()
levellist.append(NavObject("#", "Roles"))
levellist.append(NavObject("#", "Assets"))
levellist.append(NavObject('#', "Class Associations"))
levellist.append(NavObject('#', "Attackers"))
levellist.append(NavObject('#', "Threats"))
levellist.append(NavObject('#', "Vulnerabilities"))
levellist.append(NavObject('#', "Risks"))
levellist.append(NavObject('#', "Responses"))
levellist.append(NavObject('#', "Countermeasures"))
levellist.append(NavObject('#', "Security Patters"))
risk.setmultilevel(levellist)

iris = NavObject("#", "IRIS")
iris.setIcon("fa fa-eye")
levellist = list()
levellist.append(NavObject("#", "Find"))
levellist.append(NavObject("#", "Environments"))
levellist.append(NavObject('#', "Personas"))
levellist.append(NavObject('#', "Tasks"))
levellist.append(NavObject('#', "External Documents"))
levellist.append(NavObject('#', "Document References"))
levellist.append(NavObject('#', "Concept References"))
levellist.append(NavObject('#', "Persona Characteristics"))
levellist.append(NavObject('#', "Task Characteristics"))
iris.setmultilevel(levellist)

eu = NavObject("#", "EUSTACE")
eu.setIcon("fa fa-codepen")
levellist = list()
levellist.append(NavObject("#", "Internal Documents"))
levellist.append(NavObject("#", "Codes"))
levellist.append(NavObject('#', "Quotations"))
levellist.append(NavObject('#', "Code Network"))
levellist.append(NavObject('#', "Implied Processes"))
eu.setmultilevel(levellist)

options = NavObject("#", "Options")
options.setIcon("fa fa-wrench")
levellist = list()
levellist.append(NavObject("#", "Asset Values"))
levellist.append(NavObject("#", "Asset Types"))
levellist.append(NavObject('#', "Access rights"))
levellist.append(NavObject('#', "Protocols"))
levellist.append(NavObject('#', "Privileges"))
levellist.append(NavObject('#', "Surface Types"))
levellist.append(NavObject('#', "Vulnerability Types"))
levellist.append(NavObject('#', "Vulnerability Severities"))
levellist.append(NavObject('#', "Capabilities"))
levellist.append(NavObject('#', "Motivations"))
levellist.append(NavObject('#', "Threat Types"))
levellist.append(NavObject('#', "Threat Likelihoods"))
levellist.append(NavObject('#', "Threat values"))
levellist.append(NavObject('#', "Risk values"))
levellist.append(NavObject('#', "Template Assets"))
levellist.append(NavObject('#', "Template Requirements"))
levellist.append(NavObject('#', "Countermeasure values"))
options.setmultilevel(levellist)

view = NavObject("#", "View")
view.setIcon("fa fa-square-o")
levellist = list()
levellist.append(NavObject("#", "Risk Analysis"))
levellist.append(NavObject("#", "Asset Model"))
levellist.append(NavObject('#', "Goal Model"))
levellist.append(NavObject('#', "Obstacle Model"))
levellist.append(NavObject('#', "Responsibility Model"))
levellist.append(NavObject('#', "Task Model"))
levellist.append(NavObject('#', "Assumption Model"))
levellist.append(NavObject('#', "Assumption Task Model"))
levellist.append(NavObject('#', "Traceability"))
view.setmultilevel(levellist)

grid = NavObject("#", "Grid")
grid.setIcon("fa fa-th")
levellist = list()
levellist.append(NavObject("#", "Requirements"))
levellist.append(NavObject("#", "Goals"))
levellist.append(NavObject('#', "Obstacles"))
levellist.append(NavObject('#', "Relabel Objects"))
grid.setmultilevel(levellist)

help = NavObject("#", "Help")
help.setIcon("fa fa-question")
levellist = list()
levellist.append(NavObject("#", "About"))
help.setmultilevel(levellist)

navList = list()
navList.append(file)
navList.append(req)
navList.append(risk)
navList.append(iris)
navList.append(eu)
navList.append(options)
navList.append(view)
navList.append(grid)
navList.append(help)

body = """<svg height="400" width="450">
<path id="lineAB" d="M 100 350 l 150 -300" stroke="red" stroke-width="3" fill="none" />
  <path id="lineBC" d="M 250 50 l 150 300" stroke="red" stroke-width="3" fill="none" />
  <path d="M 175 200 l 150 0" stroke="green" stroke-width="3" fill="none" />
  <path d="M 100 350 q 150 -300 300 0" stroke="blue" stroke-width="5" fill="none" />
  <!-- Mark relevant points -->
  <g stroke="black" stroke-width="3" fill="black">
    <circle id="pointA" cx="100" cy="350" r="3" />
    <circle id="pointB" cx="250" cy="50" r="3" />
    <circle id="pointC" cx="400" cy="350" r="3" />
  </g>
  <!-- Label the points -->
  <g font-size="30" font="sans-serif" fill="black" stroke="none" text-anchor="middle">
    <text x="100" y="350" dx="-30">A</text>
    <text x="250" y="50" dy="-10">B</text>
    <text x="400" y="350" dx="30">C</text>
  </g>
  Sorry, your browser does not support inline SVG.
</svg>"""


lookup = TemplateLookup(directories=['./BaseTemplates'], module_directory='./BaseTemplates_out')
template = lookup.get_template("index.html")
"""print(template.render(navList=navList,title="CAIRIS Web App", body=body))"""

temp_file = open("./public/index.html","w")
temp_file.write(template.render(navList=navList,title="CAIRIS Web App", body=body))
temp_file.close()
print("File created/altered (index.html)")
"""webbrowser.open('file://' + os.path.realpath('./public/index.html'));"""

def serve_template(templatename, **kwargs):
    mytemplate = lookup.get_template(templatename)
    print(mytemplate.render(**kwargs))