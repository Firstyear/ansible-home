{% for item in groups['DailySet1'] %}
echo ---- STATUS {{ item }} ----
rdiff-backup --list-increments /home/backup/{{ item }} ;true
echo ---- END {{ item }} ----

{% endfor %}
