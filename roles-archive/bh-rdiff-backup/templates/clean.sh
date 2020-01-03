{% for item in groups['DailySet1'] %}
echo ---- CLEAN {{ item }} ----
rdiff-backup --force --remove-older-than 1W /home/backup/{{ item }}/ ;true
echo ---- END {{ item }} ----

{% endfor %}

