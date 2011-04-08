<? include("vars.php"); ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/> 
		<link rel="stylesheet" href="styles.css" type="text/css"/>
		<title>nametrans</title>
	</head>
	<body>
		<div class="downloadbar">
			<div class="downloadbox">
				<div class="downloadtitle">
					<a href="<? echo $nametrans_gui_url ?>">Download</a>
				</div>
				<div>terminal and gui <em>(<? echo $nametrans_gui_filesize ?>)</em></div>
			</div>
			<div class="downloadother">
				<a href="https://sourceforge.net/projects/nametrans/files/">Other downloads</a>
			</div>

			<div class="downloadbox">
				<div class="downloadtitle">
					<a href="<? echo $nametrans_terminal_url ?>">Download</a>
				</div>
				<div>terminal only <em>(<? echo $nametrans_terminal_filesize ?>)</em></div>
			</div>
			<div class="downloadother">
				<a href="https://sourceforge.net/projects/nametrans/files/">Other downloads</a>
			</div>
		</div>

		<div class="title">nametrans</div>
		<div class="subtitle">
			Why rename one file at a time?<br/>
			<span style="padding-right: 40px;"></span>When you can do them all at once?
		</div>

		<div class="block">
			<div class="ss">
				<img alt="ss-term" src="ss-term.png"/>
			</div>
			<div class="textblock">
				<h1>Rename with patterns</h1>
				<p> Renaming a file works well when there is just one. But when you
				have a directory full of them it gets tedious quickly.
				</p>
				<p>With <span class="code">nametrans</span> you can use search
				and replace on your list of files as you would on text in a
				document.
				</p>
				<p>And with regular expressions you have even more power to
				transform file names (and whole file paths)
				systematically.
				</p>
				<p>With useful presets for common fixes like lowercasing or capitalization you
				can keep your filenames nice and tidy, whether 10 or 10,000 of
				them, in one go.
				</p>
			</div>
		</div>

		<div class="block">
			<div class="ss">
				<img alt="ss-gui" src="ss-gui.png"/>
			</div>
			<div class="textblock">
				<h1>Requirements</h1>
				<p>To run the gui program you need a .NET runtime (2.0 or
				later) and
				<a href="http://www.mono-project.com/GtkSharp">Gtk#</a>.
				</p>
				<ul>
					<li>On Ubuntu everything should be preinstalled except for the package
					<span class="code">libmono-i18n2.0-cil</span>.
					</li>
					<li>On Fedora you should get all the required dependencies
					by installing the packages <span class="code">gtk-sharp2</span> and
					<span class="code">mono-locale-extras</span>.
					</li>
					<li>On Windows Vista and Windows 7 .NET comes preinstalled, so
					you just need <a
						href="http://www.go-mono.com/mono-downloads/download.html">Gtk#</a>.
					</li>
					<li>On Windows XP you can install either <a
						href="http://www.microsoft.com/net/download.aspx">.NET</a>
					and <a
						href="http://www.go-mono.com/mono-downloads/download.html">Gtk#</a>,
					or <a
						href="http://www.go-mono.com/mono-downloads/download.html">Mono</a>
					(includes Gtk#).
					</li>
					<li>On Mac OS X you need to install <a
						href="http://www.go-mono.com/mono-downloads/download.html">Mono</a> (untested).
					</li>
				</ul>
				<p>To run the terminal program you need <a
					href="http://www.python.org/">Python</a> or <a
					href="http://www.ironpython.net/">IronPython</a>.
				</p>
			</div>
		</div>

		<div class="block"></div>
	</body>
</html>
