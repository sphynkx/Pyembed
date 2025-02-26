<?php

require_once __DIR__ . '/../Pyembed.constants.php';

use MediaWiki\Revision\RevisionRecord;
use MediaWiki\Revision\SlotRecord;
use MediaWiki\MediaWikiServices;
use MediaWiki\EditPage\EditPage;


class PyembedHooks {
    public static function onParserFirstCallInit( Parser $parser ) {
        $parser->setFunctionHook( 'pyembed', [ self::class, 'renderPyembed' ] );
    }

    public static function onBeforePageDisplay( OutputPage &$out, Skin &$skin ) {
        global $wgCodeHighlightMethod, $wgPyembedDebugMode;

        $title = $out->getTitle();
        if ( $title->getNamespace() === NS_PYEMBED ) {
            $action = $out->getRequest()->getVal('action', 'view');
            if ( $action === 'view' ) {
                $revisionStore = MediaWikiServices::getInstance()->getRevisionStore();
                $revision = $revisionStore->getRevisionByTitle( $title );
                if ( !$revision ) {
                    return true;
                }
                $contentObject = $revision->getContent( SlotRecord::MAIN );
                $code = $contentObject->getNativeData();

                $highlightedCode = self::highlightCode($code);

                // Remove unnecessary tags and placeholders
                $highlightedCode = preg_replace('/<div class="highlight"><pre><span><\/span>/', '', $highlightedCode);
                $highlightedCode = preg_replace('/<\/pre><\/div>/', '', $highlightedCode);

                // TODO: Configure caption text via LocalSettings.php
                $captionText = "<a href=\"/$title?action=purge\">" . wfMessage('pyembed-purge-caption')->plain() . "</a> " . wfMessage('pyembed-purge-caption-page')->plain() . ".";
                $class = ($wgCodeHighlightMethod === 'pygments') ? 'pygments' : '';
                $codeWithLineNumbers = "<pre class='line-numbers language-python $class'><code class='language-python'>$highlightedCode</code></pre>";

                $out->clearHTML();
                $out->addHTML("$captionText$codeWithLineNumbers");
                $out->addModules(['ext.pyembed.styles', 'ext.pyembed.scripts']);
            }
        }

        // Transmit wgPyembedDebugMode to JavaScript
        $out->addJsConfigVars('wgPyembedDebugMode', $wgPyembedDebugMode);

        return true;
    }


    public static function onBeforePageDisplayAddCodeReset( OutputPage &$out, Skin &$skin ) {
        $out->addInlineStyle('.prism-code { all: unset; display: inline; } .prev_reset { padding: 0 !important; font-family: inherit !important; background-color: transparent !important; box-shadow: none !important; display: inline !important; }');
        return true;
    }


    public static function beforeEditButtons( EditPage $editpage, array &$buttons, &$tabindex ) {
        if ( $editpage->getTitle()->getNamespace() === NS_PYEMBED ) {
            unset( $buttons['preview'] );
        }
        return true;
    }


	public static function renderPyembed(Parser $parser, $module = '', ...$params) {
		global $wgPyembedDebugMode, $wgPyembedAllowedModules;

		if (!isset($wgPyembedAllowedModules)) {
			$wgPyembedAllowedModules = [];
		}

		error_log("Value of wgPyembedDebugMode in renderPyembed: " . $wgPyembedDebugMode);

		$title = Title::newFromText("Pyembed:$module");
		if (!$title || !$title->exists()) {
			return "<span style='color:red;'>" . wfMessage('pyembed-scriptpage-notfound', "$module")->plain() . "</span><br>";
		}

		$wikiPage = WikiPage::factory($title);
		$revision = $wikiPage->getRevisionRecord();
		if (!$revision) {
			return "<span style='color:red;'>" . wfMessage('pyembed-no-content-found', "$module")->plain() . "</span><br>";
		}
		$contentObject = $revision->getContent(SlotRecord::MAIN);
		$code = $contentObject->getNativeData();

		$function = '';
		$additionalDataArray = []; // Array to store func params (from request)
		$markupMode = 'html'; // Default value
		$inputParams = []; // Array to store params from 'input'
		$processedInput = '';

		error_log("Params: " . print_r($params, true));

		// Detect func name in first elem of array
		if (!empty($params) && strpos($params[0], 'input') !== 0 && strpos($params[0], 'markup') !== 0) {
			$function = array_shift($params);
		}

		// Fix func name detection for markup issue
		if (preg_match('/markup:/', $function)) {
			$markupMode = substr($function, 7);
			$function = '';
		}

		// Sandbox for test "input" content
		$inputValidatorScript = __DIR__ . '/../sandbox/sandbox_input.py';

		foreach ($params as $param) {
			error_log("Processing param: $param");
			if (strpos($param, 'input:') === 0) {
				error_log("Found input param: $param");
				$inputLines = trim(substr($param, 6));
				$inputLinesBase64 = base64_encode($inputLines); // Encode in base64 to save all formating
				// echo "<p><br><p><br><p><br>\$inputLinesBase64=$inputLinesBase64 ; ".print_r($inputLinesBase64,true);
				$command = "python " . escapeshellarg($inputValidatorScript) . " " . escapeshellarg($inputLinesBase64) . " 2>&1";
				$insandoutpArray = [];
				$returnVar = null;
				exec($command, $insandoutpArray, $returnVar);

				error_log("\$inputLinesBase64=" . print_r($inputLinesBase64, true) . print_r($insandoutpArray, true));

				if ($returnVar !== 0) {
					return "<span style='color:red; font-weight: bold;'>" . wfMessage('pyembed-input-error')->plain() . "</span>";
				}

				$processedInput .= implode("\n", $insandoutpArray) . "\n";
			} elseif (strpos($param, 'markup:') === 0) {
				$markupMode = substr($param, 7);
			} else {
				$additionalDataArray[] = $param;
			}
		}

		$additionalData = implode(', ', $additionalDataArray);
		error_log("Function additionalData detected: $additionalData");

		// Run func with or w/o params - if params detected
		if (!empty($function)) {
			error_log("Function parameter detected: $function");
			if (!empty($additionalData)) {
				$code = $processedInput . $code . "\n\nif __name__ == '__main__':\n    $function($additionalData)";
			} else {
				$code = $processedInput . $code . "\n\nif __name__ == '__main__':\n    $function()";
			}
		} else {
			error_log("No function parameter detected");
			$code = $processedInput . $code;
		}

		error_log("Final generated code: $code");

		$debugMode = $wgPyembedDebugMode ? 'True' : 'False';
		error_log("Debug mode from LocalSettings.php: " . $debugMode);

		// Remake PHP array to Python dict
		$allowedModulesArray = [];
		foreach ($wgPyembedAllowedModules as $module => $objects) {
			$allowedModulesArray[] = "'$module': {" . implode(", ", array_map(fn($obj) => "'$obj'", $objects)) . "}";
		}
		$allowedModulesString = "{" . implode(", ", $allowedModulesArray) . "}";

		$result = self::executePythonCode($code, $debugMode, $inputParams, $allowedModulesString);

		if ($wgPyembedDebugMode) {
			if (preg_match('/wiki/', $markupMode)) {
				$result = "[https://{{SERVERNAME}}/{{NAMESPACE}}:{{PAGENAMEE}}?action=purge " . wfMessage('pyembed-purge-debug')->plain() . "]<br>\n\n" . $result;
			} else {
				$result = "<a href=\"?action=purge\">" . wfMessage('pyembed-purge-debug')->plain() . "</a><br>" . $result;
			}
		}

		if (preg_match('/wiki/', $markupMode)) {
			$result = $parser->recursiveTagParse($result);
			$result = Html::rawElement('div', null, $result);
			return [$result, 'noparse' => true, 'isHTML' => true];
		} else {
			return [$result, 'noparse' => true, 'isHTML' => true];
		}
	}


	private static function executePythonCode( $code, $debugMode, $inputParams = [], $allowedModules = [] ) {
		// Add "input" content into beginning of temp. script
		$globalVarsCode = "";
		foreach ($inputParams as $key => $value) {
			$globalVarsCode .= "$key = $value\n";
		}

		$code = $globalVarsCode . $code;

		$tempFile = tempnam(sys_get_temp_dir(), 'pyembed_');
		file_put_contents($tempFile, $code);

		if ($debugMode == 'True') {
			error_log("Temp file: " . $tempFile);
			error_log("Code in file: " . file_get_contents($tempFile));
		}

		$sandboxScript = __DIR__ . '/../sandbox/sandbox.py';
		// Convert the allowed modules to a JSON string
		$allowedModulesString = escapeshellarg(json_encode($allowedModules));
		$paramString = implode(' ', array_map(function($key, $value) {
			return escapeshellarg("$key=$value");
		}, array_keys($inputParams), $inputParams));
		$command = "python $sandboxScript " . escapeshellarg($tempFile) . " " . escapeshellarg($debugMode) . " $allowedModulesString $paramString";
////echo "<p><br><p><br><p><br>\$allowedModulesString=$allowedModulesString ; <br>\$command=$command";
		if ($debugMode == 'True') {
			$command .= " 2>&1";
			error_log("Command to be executed: " . $command);
		} else {
			$command .= " 2>/dev/null";
		}

		$output = [];
		$returnVar = null;

		exec($command, $output, $returnVar);

		if ($debugMode == 'True') {
			error_log("Command: " . $command);
			error_log("Output: " . implode("\n", $output));
			error_log("Return value: " . $returnVar);
		}

		if ($debugMode == 'False') {
			unlink($tempFile);
		}

		// echo "<p><br><p><br><p><br>\$returnVar=$returnVar ; ".print_r($output,true);

		if($returnVar === 5) {
/////echo "<p><br><p><br><p><br>\$returnVar=$returnVar ; ".print_r($output,true);
			preg_match('/Error: Restricted method: (.*?) not in .*/', $output[0], $matches);
			return "<span style='color:red; font-weight:bold;'>" . wfMessage('pyembed-method-restricted', $matches[1])->plain() . "</span>";
		} elseif($returnVar === 4) {
			preg_match('/Error: Restricted attribute: (.*?) from (.*?) module/', $output[0], $matches);
			return "<span style='color:red; font-weight:bold;'>" . wfMessage('pyembed-attribute-restricted', $matches[1], $matches[2])->plain() . "</span>";
		} elseif ($returnVar === 3) {
			$restrictedModule = preg_replace('/Error: Restricted module: /', '', $output[0]);
			return "<span style='color:red; font-weight:bold;'>" . wfMessage('pyembed-module-restricted', $restrictedModule)->plain() . "</span>";
		} elseif ($returnVar === 2) {
			$missingModule = preg_replace('/Error: Missing module: /', '', $output[0]);
			return "<span style='color:red; font-weight:bold;'>" . wfMessage('pyembed-module-notfound', $missingModule)->plain() . "</span>";
		} elseif ($returnVar === 1) {
			return "<span style='color:red; font-weight:bold;'>" . wfMessage('pyembed-execute-error')->plain() . ".</span><br>" . implode('<br>', $output);
		} else {
			$commandOutput = implode('<br>', $output);
			return $commandOutput;
		}
	}


	private static function highlightCode($code) {
		$escapedCode = htmlspecialchars($code, ENT_NOQUOTES, 'UTF-8');
		// Syntax highlighting using Prism.js
		$highlightedCode = "<pre class='line-numbers'><code class='language-python'>$escapedCode</code></pre>";
		if ($debugMode == 'True') {
			error_log($highlightedCode);
		}
		return $highlightedCode;
	}


	public static function onCanonicalNamespaces( array &$namespaces ) {
		$namespaces[NS_PYEMBED] = 'Pyembed';
		$namespaces[NS_PYEMBED_TALK] = 'Pyembed_talk';
	}
}

$wgHooks['CanonicalNamespaces'][] = 'PyembedHooks::onCanonicalNamespaces';
?>
