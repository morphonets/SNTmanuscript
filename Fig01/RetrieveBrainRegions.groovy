#@UIService ui

import sc.fiji.snt.annotation.*
import org.scijava.table.DefaultGenericTable

scope = AllenUtils.getCompartment("grey")
maxDepth = 7

table = new DefaultGenericTable()
table.appendColumn("ID")
table.appendColumn("Name")
table.appendColumn("Abbrev")

for (c in scope.getChildren()) {
	if (c.isMeshAvailable() && c.getOntologyDepth() <= maxDepth) {
		table.appendRow()
		table.set("ID", table.getRowCount()-1, c.id())
		table.set("Name", table.getRowCount()-1, c.name())
		table.set("Abbrev", table.getRowCount()-1, c.acronym())
	}
}
ui.show("Brain Regions", table)
