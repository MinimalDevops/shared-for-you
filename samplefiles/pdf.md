{% if summarized_content == 'true' %}
summary
{% endif %}
{% if pdf == 'true' %}
??? note "Checkout the PDF"
      ![PDF](pdf/Name.pdf){ type=application/pdf style='min-height:100vh;width:100%' }
 {% endif %}