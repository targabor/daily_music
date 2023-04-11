@echo off

echo "starting daily extraction"
curl http://localhost:5001/extract_data
curl http://localhost:5000/get_id_for_youtube_songs
curl http://localhost:5000/get_data_for_tracks
curl http://localhost:5000/get_data_for_artists
echo "daily extraction done"