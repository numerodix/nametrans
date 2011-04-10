<?php 
	$nametrans_terminal_filename = "nametrans-terminal-0.1pre15.zip";
	$nametrans_terminal_filesize = "23kb";

	$nametrans_gui_filename = "nametrans-gui-0.1pre15.zip";
	$nametrans_gui_filesize = "2.3mb";

	$nametrans_guiwin_filename = "nametrans-guiwin-0.1pre15.zip";
	$nametrans_guiwin_filesize = "10mb";

	if (eregi("windows", $_SERVER['HTTP_USER_AGENT'])) {
		$nametrans_gui_filename = $nametrans_guiwin_filename;
		$nametrans_gui_filesize = $nametrans_guiwin_filesize;
	}

	$nametrans_terminal_url = "http://downloads.sourceforge.net/nametrans/$nametrans_terminal_filename";
	$nametrans_gui_url = "http://downloads.sourceforge.net/nametrans/$nametrans_gui_filename";
?>
