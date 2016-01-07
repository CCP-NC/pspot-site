<?php

    // Don't allow random users to just wander in
    define('IS_AJAX', isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest');
    if(!IS_AJAX) {die('Restricted access');}

    $MAX_SAFE_LOOPS = 20; // Max loops when reading file

    // Now build a pseudopotential list, classified by element
    $pspot_dir = "data/pspot";
    $pspot_raw = array_diff(scandir($pspot_dir), array('.', '..'));

    $pspot = array("errlog"=>"");

    foreach ($pspot_raw as $pspot_file) {
        $pspot_split = explode("_", $pspot_file, 2);
        $pspot_path = $pspot_dir . "/" . $pspot_file;
        $elem = $pspot_split[0];
        // Extract cutoff energies and XC functional
        $pspot_f = fopen($pspot_path, "r");
        // Start reading
        $xc = ""; $cutoff = 0;
        $cut_tag = "FINE";
        $xc_tag = "Level of theory:";
        for ($i = 0; $i < $MAX_SAFE_LOOPS; ++$i) {
            $line = fgets($pspot_f);
            $pspot["errlog"] = $pspot["errlog"] . $line;
            $cut_pos = strpos($line, $cut_tag);
            if ($cut_pos !== false) {
                $line_split = explode(" ", trim($line), 2);
                $cutoff = intval($line_split[0]);
                $pspot["errlog"] = $pspot["errlog"] . $line_split[0] . "\n";
            }
            // Then we expect XC functional
            $xc_pos = strpos($line, $xc_tag);
            if ($xc_pos !== false) {
                $line_split = explode(" ", trim(substr($line, $xc_pos+strlen($xc_tag))), 2);
                $xc = $line_split[0];
                $pspot["errlog"] = $pspot["errlog"] . $line_split[0] . "\n";
                break;
            }
        }
        if (array_key_exists($elem, $pspot)) {
            $pspot[$elem][] = array("path"=>$pspot_path, "file"=>$pspot_file, "cutoff"=>$cutoff, "xc"=>$xc);
        }
        else {
            $pspot[$elem] = array(array("path"=>$pspot_path, "file"=>$pspot_file, "cutoff"=>$cutoff, "xc"=>$xc));
        }
        if ($pspot_split[1] == 'OTF.usp') {
            $pspot[$elem]["default"] = array("path"=>$pspot_path, "file"=>$pspot_file, "cutoff"=>$cutoff, "xc"=>$xc);
        }
    }

    echo json_encode($pspot);
?>