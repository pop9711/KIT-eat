// JSON API의 URL
const apiUrl = 'http://52.78.214.179/data_test';

// Fetch를 사용하여 데이터 가져오기
fetch(apiUrl)
  .then(response => response.json())
  .then(result => {
    const dataList = result.data;

    // 카카오맵 초기화
    const mapContainer = document.getElementById('map');
    const options = {
      center: new kakao.maps.LatLng(35.147206359654085, 129.0119992573746), // 초기 지도 중심 좌표 (서울)
      level: 5, // 초기 지도 확대 레벨
    };
    const map = new kakao.maps.Map(mapContainer, options);

    // 주소를 좌표로 변환하여 마커 생성 및 표시
    const geocoder = new kakao.maps.services.Geocoder();

    // 현재 열린 인포윈도우를 저장할 변수
    let currentInfowindow = null;

    dataList.forEach(data => {
      const address = data.address;
      const name = data.name;

      geocoder.addressSearch(address, function(result, status) {
        if (status === kakao.maps.services.Status.OK) {
          const markerPosition = new kakao.maps.LatLng(result[0].y, result[0].x);

          // 마커 생성
          const marker = new kakao.maps.Marker({
            position: markerPosition,
            title: name,
          });

          // 인포윈도우 생성
          const infowindow = new kakao.maps.InfoWindow({
            content: '<div style="padding:5px; text-align:center;">' + name + '</div>',
          });

          // 마커 클릭 이벤트 처리
          kakao.maps.event.addListener(marker, 'click', function() {
            // 현재 열려있는 인포윈도우 닫기
            if (currentInfowindow) {
              currentInfowindow.close();
            }

            // 새로운 인포윈도우 열기
            infowindow.open(map, marker);

            // 현재 열린 인포윈도우 갱신
            currentInfowindow = infowindow;
          });


          // 마커 지도에 표시
          marker.setMap(map);

          // 모든 마커가 표시되도록 지도의 범위 설정
          const bounds = new kakao.maps.LatLngBounds();
          bounds.extend(markerPosition);
          map.setBounds(bounds);
        }
      });
    });

    // 지도 클릭 시 현재 열린 인포윈도우 닫기
    kakao.maps.event.addListener(map, 'click', function() {
      if (currentInfowindow) {
        currentInfowindow.close();
        currentInfowindow = null;
      }
    });
  })

  
  .catch(error => {
    // 오류 처리
    console.error('데이터 가져오기 오류:', error);
  });