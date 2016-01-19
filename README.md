# slideshare-vpn
선린인터넷고등학교 Flask 소수 전공 프로젝트.
<http://slideshare.net> 이 학교에서 접속이 안돼서 슬라이드 다운받아보려고 만든 서비스 입니다.


## flower에서 task 못받아오는 경우
<https://github.com/mher/flower/issues/445>
아직 패치가 릴리즈 되지 않음, 고로
직접 site-packages/flower/utils/tasks.py 를 열어서
<https://github.com/mher/flower/commit/79ef3fe160322781f567bbf88a3289803d1fe2e7>
처럼 수정.
