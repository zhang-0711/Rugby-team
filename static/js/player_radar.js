// player_radar.js
// Requires ECharts to be loaded on the page

// 通用雷达图渲染
function renderPlayerRadarChart(domId, indicators, values, skillType) {
    var chartDom = document.getElementById(domId);
    var myChart = echarts.init(chartDom);
    var option = {
        title: {
            text: skillType + ' Skills',
            left: 'center',
            textStyle: { fontSize: 16 }
        },
        tooltip: {},
        radar: {
            indicator: indicators.map(function(name) { return { name: name, max: 5 }; }),
            center: ['50%', '55%'],
            radius: 80
        },
        series: [{
            name: skillType + ' Skill',
            type: 'radar',
            data: [
                {
                    value: values,
                    name: skillType
                }
            ],
            areaStyle: { opacity: 0.3 }
        }]
    };
    myChart.setOption(option);
    return myChart;
}

// 切换雷达图
function switchRadarChart(playerKey, skillType, skillData) {
    var skillMap = {
        'Passing': ['Standard', 'Spin', 'Pop'],
        'Tackling': ['Front', 'Rear', 'Side', 'Scrabble'],
        'Kicking': ['Drop', 'Punt', 'Grubber', 'Goal']
    };
    var indicators = skillMap[skillType];
    var values = indicators.map(function(name) {
        return skillData && skillData[name] !== undefined ? skillData[name] : 0;
    });
    renderPlayerRadarChart('radar-' + playerKey, indicators, values, skillType);
}
