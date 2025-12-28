import streamlit as st
import streamlit.components.v1 as components

st.title("📈 대시보드 2 (Tableau)")
# st.caption("이곳은 두 번째 테블로 대시보드 화면입니다.")

# -----------------------------------------------------------------------------
# [사용법] Tableau Public/Cloud에서 'Share' 버튼 -> 'Copy Embed Code' 후 아래에 붙여넣기
# -----------------------------------------------------------------------------
# 예시 코드입니다. 실제 코드로 교체하세요!
tableau_embed_code = """
<div class='tableauPlaceholder' id='viz1766910297801' style='position: relative'><noscript><a href='#'><img alt='ㄹㅇ리얼대시보드ㄹㅇ ' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;04&#47;04__1227_col&#47;sheet9&#47;1_rss.png' style='border: none' /></a></noscript><object class='tableauViz'  style='display:none;'><param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> <param name='embed_code_version' value='3' /> <param name='site_root' value='' /><param name='name' value='04__1227_col&#47;sheet9' /><param name='tabs' value='no' /><param name='toolbar' value='yes' /><param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;04&#47;04__1227_col&#47;sheet9&#47;1.png' /> <param name='animate_transition' value='yes' /><param name='display_static_image' value='yes' /><param name='display_spinner' value='yes' /><param name='display_overlay' value='yes' /><param name='display_count' value='yes' /><param name='language' value='ko-KR' /><param name='filter' value='publish=yes' /></object></div>                <script type='text/javascript'>                    var divElement = document.getElementById('viz1766910297801');                    var vizElement = divElement.getElementsByTagName('object')[0];                    if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1600px';vizElement.style.height='927px';} else { vizElement.style.width='100%';vizElement.style.height='1877px';}                     var scriptElement = document.createElement('script');                    scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';                    vizElement.parentNode.insertBefore(scriptElement, vizElement);                </script>
"""

# HTML 렌더링 (height를 넉넉하게 줘야 스크롤바가 안 생김)
components.html(tableau_embed_code, width=1650, height=970, scrolling=True)