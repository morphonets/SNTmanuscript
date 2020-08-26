#@UIService ui

import sc.fiji.snt.annotation.*
import sc.fiji.snt.analysis.SNTTable

scope = AllenUtils.getCompartment("grey")
maxDepth = 7

table = new SNTTable()
table.appendColumn("ID")
table.appendColumn("Name")
table.appendColumn("Abbrev")

for (c in scope.getChildren()) {
	if (c.isMeshAvailable() && c.getOntologyDepth() <= maxDepth) {
		table.appendToLastRow("ID", c.id())
		table.appendToLastRow("Name", c.name())
		table.appendToLastRow("Abbrev", c.acronym())
	}
}
ui.show("Brain Regions", table)
