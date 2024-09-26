import os
from dotenv import dotenv_values


here = os.path.dirname(__file__)


def parse_env(here, do_debug=False):
	env_file = os.path.join(here, "../.env")
	return dotenv_values(env_file)

env = parse_env(here)

def get_env(key, do_debug = False):
	global env
	if env == {}:
		env = parse_env(here)
	ret = env.get(key) or os.environ.get(key)
	if do_debug:
		logger.info(f"GOT {key}={ret}")
	return ret


vowels = ["a", "e", "i", "o", "y", "u"] #, "æ", "ø", "å"]
consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"]


def word(l):
	""" Create a random pronouncable word given the number of letters"""
	ret = ""
	for i in range(0, math.floor(l/2+1)):
		ret += random.choice(consonants)
		ret += random.choice(vowels)
		if bool(random.getrandbits(1)):
			ret += random.choice(vowels)
	return ret[:l]


def sentence(l):
	""" Create a random sentence given the number of words"""
	s=list()
	for i in range(0, l):
		s.append(word(random.randint(2,9)))
	return " ".join(s)


def hte(raw):
	return html.escape(raw).encode('ascii', 'xmlcharrefreplace').decode("utf8")


def to_html(data):
	ht=""
	frst=True
	for row in data:
		if frst:
			frst=False
			ht += "<tr>"
			for k,v in row.items():
				ht += f"<th>{hte(k)}</th>"
			ht += "</tr>"
		ht += "<tr>"
		for k,v in row.items():
			links = extract_links(v)
			if links:
				ht += "<td>"
				for name, link in links.items():
					ht += f'<a href="{link}">{name}</a>'
				ht += "</td>"
			else:
				if not has_visible_content(v):
					v="" # Skip html nonsequitur
				ht += f"<td>{hte(v)}</td>"
		ht += "</tr>"
	
	return f"""
<html>
<head>
<title>GAP test</title>
<style>
*{{
font-family:sans;
}}
table, tr, td, th{{
margin:0;
padding:0;
}}
td, th{{
padding:0.1em;
}}
td{{
background: #aaa;
text-color: #333;
}}
</style>
</head>
<body>
<table>
{ht}
</table>
</body>
</html>
"""
