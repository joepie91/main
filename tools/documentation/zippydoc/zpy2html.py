import os, argparse, sys, re

parser = argparse.ArgumentParser(description='Converts ZippyDoc source files to HTML.')

parser.add_argument('files', metavar='FILE', type=str, nargs='+',
                   help='files to convert to HTML')

args = parser.parse_args()
options = vars(args)

files = options["files"]

template = """
<!doctype html>
<html>
	<head>
		<style>
			body {
				background-color: #F5F5F5;
				font-family: sans-serif;
				margin-right: 40px;
			}

			h2, h3, h4, h5, h6, h7
			{
				margin-top: 16px;
				margin-bottom: 4px;
			}

			.children { padding-left: 40px; }

			.definition
			{
				font-weight: bold;
				margin-bottom: 32px;
			}

			.example 
			{ 
				padding: 5px 6px;
				font-weight: bold;
				font-size: 15px;
				background-color: #E6E6E6; 
				margin-top: 11px;
			}

			.example > .children
			{
				padding-top: 11px;
				padding-left: 10px;
			}

			.example > .children > h7
			{
				font-size: 13px;
			}

			h7
			{
				font-size: 14px;
				font-weight: bold;
				margin-bottom: 2px;
			}

			pre
			{
				margin-top: 0px;
				padding: 6px 7px;
				background-color: #D9D9D9;
				font-weight: normal;
				font-size: 13px;
			}

			dl
			{
				margin: 5px 0px;
			}

			dt
			{
				font-weight: bold;
			}

			dd
			{
				font-size: 14px;
				font-weight: normal;
				margin-left: 8px;
			}

			.exclamation
			{
				padding: 7px 8px;
				margin: 11px 0px;
				background-color: #FFE9AA;
				border: 1px solid yellow;
				font-size: 15px;
				font-weight: normal;
			}

			.text
			{
				font-size: 15px;
				font-weight: normal;
				margin-bottom: 14px;
				margin-top: 10px;
			}

			.toc
			{
				border: 1px solid gray;
				background-color: #E6E6E6;
				padding: 8px 9px;
				font-size: 15px;
				margin-bottom: 12px;
			}

			.toc h2
			{
				margin: 0px 0px 3px 0px;
				font-size: 19px;
			}

			.toc ul
			{
				margin-top: 0px;
				margin-bottom: 0px;
				padding-left: 25px;
			}

			.toc li
			{
				margin-bottom: 2px;
			}

			.toc .alternatives
			{
				font-size: 12px;
			}

			.toc a
			{
				color: #292722;
			}

			.toc a:hover
			{
				color: black;
			}
			
			.fixed
			{
				font-family: monospace;
				background-color: white;
				padding: 1px 4px;
				border: 1px solid silver;
				border-radius: 4px;
			}
		</style>
	</head>
	<body>
		%s
	</body>
</html>
"""

class TreeLevel:
	def __init__(self, indentation, data):
		self.elements = []
		self.indentation = indentation
		self.data = data
	
	def add(self, element):
		self.elements.append(element)
		
	def output(self):
		return self.render()
		
	def render_children(self):
		child_output = ""
		
		for child in self.elements:
			child_output += child.output()
			
		return '<div class="children">%s</div>' % child_output
		
	def process_inline_markup(self, text):
		text = re.sub("`([^`]+)`", '<span class="fixed">\\1</span>', text)                         # Emphasized
		text = re.sub("\*\*([^*]+)\*\*", "<em>\\1</em>", text)                         # Emphasized
		text = re.sub("__([^_]+)__", "<strong>\\1</strong>", text)                     # Strong
		text = re.sub("{>([^}]+)}\(([^)]+)\)", '<a href="\\1.html">\\2</a>', text)     # Hyperlink with text
		text = re.sub("{>([^}]+)}", '<a href="\\1.html">\\1</a>', text)                # Hyperlink
		text = re.sub("{([^}]+:[^}]+)}\(([^)]+)\)", '<a href="\\1">\\2</a>', text)     # External hyperlink with text
		text = re.sub("{([^}]+:[^}]+)}", '<a href="\\1">\\1</a>', text)                # External hyperlink
		text = re.sub("{<([^}]+)}\(([^)]+)\)", '<a href="\\1">\\2</a>', text)     # Forced external hyperlink with text
		text = re.sub("{<([^}]+)}", '<a href="\\1">\\1</a>', text)                # Forced external hyperlink
		
		return text
		
	def fix_preformatted(self, text):
		return text.replace("<", "&lt;").replace(">", "&gt;")
		
	def clear_markup(self, text):
		return re.sub("\*\*([^*]+)\*\*", "\\1", text)
		
	def render(self):
		return self.render_children()

class Example(TreeLevel):
	def render(self):
		return '<div class="example">Example: %s %s</div>' % (self.data, self.render_children())
	
class Code(TreeLevel):
	def render(self):
		return '<h7>Code:</h7><pre class="code">%s</pre>' % self.fix_preformatted(self.data)
	
class Output(TreeLevel):
	def render(self):
		return '<h7>Output:</h7><pre class="output">%s</pre>' % self.fix_preformatted(self.data)
	
class Definition(TreeLevel):
	def get_anchor(self):
		first = self.clear_markup(self.data.splitlines()[0])
		anchor = first.replace("...", "")
		anchor = anchor.replace(".", "_")
		anchor = re.sub("[^a-zA-Z0-9_]", "", anchor)
		return anchor
	
	def get_description(self):
		for element in self.elements:
			if element.__class__.__name__ == "Text":
				data = self.process_inline_markup(element.data)
				
				if len(data) > 80:
					matches = re.match("^(.{0,80})\W", data)					
					return matches.group(1) + "..."
				else:
					return data
				
		return ""
	
	def render(self):
		return '<div class="definition"><a name="def_%s">%s %s</a></div>' % (self.get_anchor(), self.process_inline_markup(self.data.replace("\n", "<br>")), self.render_children())
	
class Exclamation(TreeLevel):
	def render(self):
		return '<div class="exclamation"><strong>Important:</strong> %s</div>' % self.process_inline_markup(self.data)
	
class Argument(TreeLevel):
	def __init__(self, indentation, data, argname):
		self.elements = []
		self.indentation = indentation
		self.argname = argname
		self.data = data
	
	def render(self):
		return '<dl><dt>%s</dt><dd>%s</dd></dl>' % (self.argname, self.process_inline_markup(self.data))
	
class Header(TreeLevel):
	def __init__(self, indentation, data, depth):
		self.elements = []
		self.indentation = indentation
		self.depth = depth
		self.data = data
		
	def render(self):
		if self.depth <= 7:
			title_type = "h%d" % self.depth
		else:
			title_type = "h7"
			
		return "<%s>%s</%s>" % (title_type, self.data, title_type)

class Text(TreeLevel):
	def render(self):
		return '<div class="text">%s</div>' % self.process_inline_markup(self.data)

class Index(TreeLevel):
	def render(self):
		global toc_items
		
		rendered = ""
		
		for item in toc_items:
			forms = item.data.splitlines()
			first = self.clear_markup(forms[0])
			
			if len(forms) > 1:
				rest = '<span class="alternatives">(also: ' + ', '.join(self.clear_markup(form) for form in forms[1:]) + ")</span>"
			else:
				rest = ""
			
			anchor = item.get_anchor()
			description = item.get_description()
			rendered += '<li><a href="#def_%s">%s</a> %s %s</li>' % (anchor, first, description, rest)
		
		return '<div class="toc"><h2>Table of contents</h2><ul>%s</ul></div>' % rendered

for zpy in files:
	destination = os.path.splitext(zpy)[0] + ".html"
	
	f = open(zpy, "r")
	data = f.read()
	f.close()
	
	paragraphs = re.split("\s*\n\s*\n", data)
	toc_items = []
	current_level = 0
	current_paragraph = 0
	current_elements = {0: TreeLevel(0, "root")}
	
	for paragraph in paragraphs:
		if paragraph.strip() == "":
			continue
			
		current_paragraph += 1
		indentation = len(paragraph) - len(paragraph.lstrip("\t")) + 1
		
		if indentation > current_level + 1:
			raise Exception("Invalid indentation found in paragraph %d" % current_paragraph)
		
		element_type = TreeLevel
		start = indentation - 1
		
		lines = [line[start:] for line in paragraph.splitlines()]
		
		if lines[0].startswith("#"):
			element_type = Header
			depth = len(lines[0]) - len(lines[0].lstrip("#"))
			lines[0] = lines[0].lstrip("# ")
			data = " ".join(lines)
		elif lines[0].startswith("^"):
			element_type = Definition
			lines[0] = lines[0].lstrip("^ ")
			data = "\n".join(lines)
		elif lines[0].startswith("@"):
			element_type = Example
			lines[0] = lines[0].lstrip("@ ")
			data = " ".join(lines)
		elif lines[0].startswith("$$") and current_elements[current_level].__class__.__name__ == "Code":
			current_elements[current_level].data += "\n\n" + "\n".join(lines).lstrip("$ ")
			continue
		elif lines[0].startswith("$"):
			element_type = Code
			lines[0] = lines[0].lstrip("$ ")
			data = "\n".join(lines)
		elif lines[0].startswith(">>") and current_elements[current_level].__class__.__name__ == "Output":
			current_elements[current_level].data += "\n\n" + "\n".join(lines).lstrip("> ")
			continue
		elif lines[0].startswith(">"):
			element_type = Output
			lines[0] = lines[0].lstrip("> ")
			data = "\n".join(lines)
		elif lines[0].startswith("!"):
			element_type = Exclamation
			lines[0] = lines[0].lstrip("! ")
			data = " ".join(lines)
		elif re.match(".*::\s*$", lines[0]):
			element_type = Argument
			argname = lines[0][:-2]
			data = " ".join(line.lstrip() for line in lines[1:])
		elif lines[0].strip() == "{TOC}":
			element_type = Index
			data = ""
		else:
			element_type = Text
			data = " ".join(lines)
			
		#print "Found element of type %s at indentation %d with data %s" % (element_type.__name__, indentation, data[:80])
			
		if element_type.__name__ == "Header":
			element = Header(indentation, data, depth)
		elif element_type.__name__ == "Argument":
			element = Argument(indentation, data, argname)
		else:
			element = element_type(indentation, data)
		
		if element_type.__name__ == "Definition":
			toc_items.append(element)
		
		current_elements[indentation - 1].add(element)
		
		current_level = indentation
		current_elements[current_level] = element
	
	rendered = template % (current_elements[0].output())
	
	f = open(destination, "w")
	f.write(rendered)
	f.close()
	
	print "Rendered %s" % destination
