<?php 
	$nametrans_terminal_filename = "nametrans-terminal-0.1pre22.zip";
	$nametrans_terminal_filesize = "25kb";

	$nametrans_gui_filename = "nametrans-gui-0.1pre22.zip";
	$nametrans_gui_filesize = "2.3mb";

	$nametrans_wingui_filename = "nametrans-wingui-0.1pre22.zip";
	$nametrans_wingui_filesize = "10mb";

	if (eregi("windows", $_SERVER['HTTP_USER_AGENT'])) {
		$nametrans_gui_filename = $nametrans_wingui_filename;
		$nametrans_gui_filesize = $nametrans_wingui_filesize;
	}

	$nametrans_terminal_url = "http://downloads.sourceforge.net/nametrans/$nametrans_terminal_filename";
	$nametrans_gui_url = "http://downloads.sourceforge.net/nametrans/$nametrans_gui_filename";
?>
