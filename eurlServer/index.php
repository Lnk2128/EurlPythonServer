<?php

if(count($_GET) == 0)
{
    make_tutorial();
}
else
{
    make_eurl();
}


//HELPER FUNCTIONS:
function beginsWith($term, $start)
{
    return strpos($term, $start, 0) === 0;
}

function writeHiddenFields($list)
{
    foreach($list as $key => $value)
    {
        echo "<INPUT type='hidden' name='" . $key . "' value='" . $value . "'>";
        
        if($key != "DOWNLOAD" or $key == "CHANGEME")
        {
            echo $key . ": " . $value . "</br>";
        }
        
    }
}
function writeURLstring($list)
{
    $urlString = "<i> This URL can be shared to access the Canvas</i><br/>http://" . $_SERVER['SERVER_ADDR']  . ":" . $_SERVER['SERVER_PORT'] . "/eurlserver?";
    foreach($list as $key => $value)
    {
        if($key != "DOWNLOAD")
        {
            $urlString .= $key . "=" . $value . "&";
        }
    }    
    substr($urlString, 0, -1);
    echo "<hr>" . $urlString . "</hr>";
}


//WORKHORSE FUNCTION:
function make_eurl()
{
    
    $terms = $_GET;
    
    if (!isset($terms["verNum"]))
    {
        $terms['verNum'] = 0.2;
    }
    
    if(isset($terms["jDomain"]) and !isset($terms["jID"]))
    {
        $ref;
        foreach(getallheaders() as $key => $val)
        {
            if($key == "Referer")
            {
                $ref = $val;
            }
        }
        
    
        if(isset($ref))
        {
            
            if( beginsWith($ref, "http://129.21.142.226:8080") or
                beginsWith($ref, "https://jira.acme-edge.com") )
                {
                    
                    $ref = explode("?", $ref); $ref = $ref[0];
                    $ref = explode("#", $ref); $ref = $ref[0];
                    
                    if(substr($ref, -1) == "/")
                    {
                        $ref = substr($ref, 0, -1);
                    }
                    $terms["jID"] = end(explode("/", $ref));
                }
        }
    }
    
    
    
    if(isset($terms["jID"]) and !isset($terms["cName"]))
    {
        $terms["cName"] = $terms["jID"];
    }
    
    if(isset($terms["cName"]) and !isset($terms["DOWNLOAD"]))
    {
        header("Content-type: application/octet-stream");
        $cleanName = $terms['cName'];
        $cleanName = str_replace(" ", "_", $cleanName);
        header("Content-Disposition: attachment; filename=" . $cleanName . ".eurl");

        echo json_encode($terms);
    }
    else
    {
    
        header("Content-type: text/html");
        echo "<FORM action='/eurlserver?' enctype='multipart/form-data' method='get'>";
        echo "<P>";

        if(isset($terms["DOWNLOAD"]) and isset($terms["cName"]) and isset($terms["edgeIp"]))
        {
            echo "<i>We're good to go!</i><hr>";
            unset($terms["DOWNLOAD"]);
            writeURLstring($terms);
            writeHiddenFields($terms);
            echo "</hr> <INPUT type='submit' value='CLICK TO DOWNLOAD'>";
        }
        else
        {
            echo "If you are reading this in the browser, you need to supply more information.<hr/>";
            echo "<INPUT type='hidden' name='DOWNLOAD' value='True'>\n";
            writeHiddenFields($terms);
            
            if(!isset($terms["cName"]))
            {
                $terms["cName"] = "CHANGEME";
            }
            if(!isset($terms["edgeIp"]))
            {
                $terms["edgeIp"] = "CHANGEME";
            }
            echo "Canvas Name : <INPUT type='text' name='cName'  value='" .  $terms["cName"]  . "'><br/>";
            echo "EdgeTable IP: <INPUT type='text' name='edgeIp'  value='" . $terms["edgeIp"] . "'><br/>";
            echo "<INPUT type='submit' value='Update Parameters'> <INPUT type='reset'>";
        }
            
        echo "</p></form>";
    }
    
    
}

//WRONG REQUEST FUNCTION:
function make_tutorial()
{


    ?>
        <h1>EDGESERVER</h1>
        If the URL starts with /eurl, and the canvas name has been supplied, we'll deliver an eurl file.
        If the canvas name is missing, we'll ask you to supply it.
        <hr>
        Deliver the File:
            http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&cName=ATable222
        </br>
        Ask for canvasName
            http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&
        </br>
        useCases:

        <ul>
            <li>
                If you go to... http://localhost:8080 you get this information.
            </li>
            <li>
                If you go to a fully qualified URL like... 
                <ul><li>... http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&cName=ATable222 
                </li><li>... you get an EURL file.</li></ul>
            </li>
            <li>
                If you need a canvasName, as with... 
                <ul><li>... http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080& 
                </li><li>... you get a form that asks for a canvasname.</li></ul>
            </li>
            <li>
                If you click the form's Submit without giving the canvas Name, you return to the form.
            </li>
            <li>
                If you do provide the canvas name to the form, you  get a CLICK to Download screen.
            </li>
            <li>
                If you go to http://localhost:8080/a_file_that_we_are_prepared_to_serve.html you'll get it.
            </li>
            <li>
                If you go to http://localhost:8080/eurl/any_inadequate_URL you'll get a cryptic warning 
            </li>
        </ul>
    <?php
    
    
}


?>