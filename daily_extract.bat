@echo off

echo ---------------------------------------------
echo starting daily extraction

echo -
echo getting tracks from slack api
REM curl http://localhost:5001/extract_data

echo -
echo matching up yputube links to spotify tracks
REM curl http://localhost:5000/get_id_for_youtube_songs

echo -
echo getting data for spotify tracks
curl http://localhost:5000/get_data_for_tracks

echo -
echo getting artists genre information
curl http://localhost:5000/get_data_for_artists

echo -
echo ---------------------------------------------
echo daily extraction done