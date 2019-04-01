{% for item in groups['DailySet1'] %}
echo ---- START {{ item }} ----
mkdir -p /home/backup/{{ item }}
rdiff-backup --ssh-no-compression --print-statistics --include-globbing-filelist /home/backup/include-list "root@{{ item }}::/" /home/backup/{{ item }}/ && \
rdiff-backup --force --remove-older-than 1W /home/backup/{{ item }}/ ;true
echo ---- END {{ item }} ----

{% endfor %}
