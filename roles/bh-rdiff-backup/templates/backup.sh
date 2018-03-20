{% for item in groups['DailySet1'] %}
echo ---- START {{ item }} ----
mkdir -p /home/backup/{{ item }}
rdiff-backup --print-statistics --include-globbing-filelist include-list "backup@{{ item }}::/" /home/backup/{{ item }}/ ;true
rdiff-backup --remove-older-than 4W /home/backup/{{ item }}/ ;true
echo ---- END {{ item }} ----

{% endfor %}
