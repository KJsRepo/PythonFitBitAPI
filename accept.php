<?php

$fp = fopen("auth_key", "w");

if($fp) {
	fwrite($fp, $_REQUEST['code']);
	fclose($fp);
}

?>
