//値をグラフに表示させる
Chart.plugins.register({
    afterDatasetsDraw: function (chart, easing) {
        var ctx = chart.ctx;

        chart.data.datasets.forEach(function (dataset, i) {
            var meta = chart.getDatasetMeta(i);
            if (!meta.hidden) {
                meta.data.forEach(function (element, index) {
                    // 値の表示
                    ctx.fillStyle = 'rgb(0, 0, 0,0.8)';//文字の色
                    var fontSize = 12;//フォントサイズ
                    var fontStyle = 'normal';//フォントスタイル
                    var fontFamily = 'Arial';//フォントファミリー
                    ctx.font = Chart.helpers.fontString(fontSize, fontStyle, fontFamily);

                    var dataString = dataset.data[index];
          
                    // 値の位置
                    ctx.textAlign = 'center';//テキストを中央寄せ
                    ctx.textBaseline = 'middle';//テキストベースラインの位置を中央揃え

                    var padding = 5;//余白
                    var position = element.tooltipPosition();
                    ctx.fillText(dataString, position.x, position.y - (fontSize / 2) - padding);
    
                });
            }
        });
    }
});


//=========== 円グラフ ============//
$('#myPieChart').on('inview', function(event, isInView) {//画面上に入ったらグラフを描画
if (isInView) {
  
var ctx = document.getElementById('myPieChart');
var chart=new Chart(ctx,{
type:'pie',//グラフのタイプ

data:{
        datasets: [{
            data: [{{p_counts.0}}+{{p_counts.1}}+{{p_counts.2}}+{{p_counts.3}}+{{p_counts.4}}+{{p_counts.5}}+{{p_counts.6}}, {{n_counts.0}}+{{n_counts.1}}+{{n_counts.2}}+{{n_counts.3}}+{{n_counts.4}}+{{n_counts.5}}+{{n_counts.6}}],
           //data: ["50","20"],
            backgroundColor: ['rgba(75,192,192,0.4)','rgba(255,99,132,0.2)']
        }],

        // These labels appear in the legend and in the tooltips when hovering different arcs
        labels: [
            'Positive',
            'Negative'
        ]
},
    
    
    
options:{//グラフのオプション
  maintainAspectRatio: false,//CSSで大きさを調整するため、自動縮小をさせない
  legend:{
    display:true//グラフの説明を表示
  },
  tooltips:{//グラフへカーソルを合わせた際の詳細表示の設定
    callbacks:{
        label: function (tooltipItem, data) {
      return data.labels[tooltipItem.index]+ ": "+ data.datasets[0].data[tooltipItem.index] + "%";//%を最後につける
    }
    },    
  },
  title:{//上部タイトル表示の設定
    display: true,
    fontSize:10,
    text: '単位：%'
  },
}
});
  
}
});