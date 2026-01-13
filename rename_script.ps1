$baseDir = "c:\Users\Marc\Documents\1G1R\Balrog Toolkit\Python - Module\Retrogaming-Toolkit-AIO"
$iconDir = "$baseDir\icons"
$readmeDir = "$baseDir\read_me"

$renames = @{
    "MaxCSO_Compression_Script" = "MaxCSO";
    "CHD_Converter_Tool" = "CHDManager";
    "rvz_iso_convert" = "DolphinConvert";
    "convert_images" = "ImageConvert";
    "YT_Download" = "YTDownloader";
    "video_converter" = "VideoConvert";
    "enable_long_paths" = "LongPaths";
    "game_batch_creator" = "GameBatch";
    "collection_builder" = "CollectionBuilder";
    "collection_extractor" = "CollectionExtractor";
    "folder_name_to_txt" = "FolderToTxt";
    "folder_to_zip" = "FolderToZip";
    "empty_generator" = "EmptyGen";
    "game_removal" = "GameRemoval";
    "gamelist_to_hyperlist" = "GamelistHyperlist";
    "hyperlist_to_gamelist" = "HyperlistGamelist";
    "install_dependencies" = "InstallDeps";
    "liste_fichier_simple" = "ListFilesSimple";
    "liste_fichier_windows" = "ListFilesWin";
    "media_orphan_detector" = "MediaOrphans";
    "folder_cleaner" = "FolderCleaner";
    "merge_story_hyperlist" = "StoryHyperlist";
    "story_format_cleaner" = "StoryCleaner";
    "m3u_creator" = "M3UCreator";
    "cover_extractor" = "CoverExtractor";
    "cbzkiller" = "CBZKiller";
    "es_systems_custom" = "SystemsExtractor";
    "assisted_gamelist_creator" = "AssistedGamelist";
}

foreach ($key in $renames.Keys) {
    $old = $key
    $new = $renames[$key]
    
    # Python files
    if (Test-Path "$baseDir\$old.py") {
        git mv "$baseDir\$old.py" "$baseDir\$new.py"
    }
    
    # Icons
    if (Test-Path "$iconDir\$old.ico") {
        git mv "$iconDir\$old.ico" "$iconDir\$new.ico"
    } else {
        Write-Host "Icon not found: $old.ico"
    }

    # Readmes
    if (Test-Path "$readmeDir\$old.txt") {
        git mv "$readmeDir\$old.txt" "$readmeDir\$new.txt"
    } else {
         Write-Host "Readme not found: $old.txt"
    }
}
