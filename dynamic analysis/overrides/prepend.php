<?php
define("__LOG_FUNCTION_PATH", "/shared/function-hooking");

foreach(scandir(__DIR__ . "/uopz/") as $file) {
		if(str_ends_with($file, ".php")) {
			include __DIR__ . "/uopz/" . $file;
		}
	}