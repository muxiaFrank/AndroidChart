<template>
  <div class="container">
    <h1>Android性能曲线</h1>
    <ve-line :data="chartData" :settings="chartSettings"></ve-line>
    <span class="badge badge-pill badge-light">Native_AVG:{{chartData.Native_AVG}}MB</span>
    <span class="badge badge-pill badge-light">Dalvik_AVG:{{chartData.Dalvik_AVG}}MB</span>
    <span class="badge badge-pill badge-light">Cpu_AVG:{{chartData.cpu_avg}}</span>
  </div>
</template>

<script>
  module.exports = {
    data(){
      return{
        chartData:{}
      }
    },
    methods:{
      getdata:function(){
        this.$http.get('static/data.json').
      then((response) => {
        response = response.body;
        console.log('数据加载成功');
        this.chartData = response;
        // this.$set(this, chartData, response);
        console.log(this.chartData);
      });
    }

    },

    
    created: function () {
      var self = this;
      // this.$http.get('static/data.json').
      // then((response) => {
      //   response = response.body;
      //   console.log('数据加载成功');
      //   this.chartData = response;
      //   // this.$set(this, chartData, response);
      //   console.log(this.chartData);
      //   console.log('数据加载成功');

      // })

      setInterval(this.getdata,1000)

      

      this.chartSettings = {
        axisSite: {right: ['cpu']},
        max: [0, 1],
        yAxisType: ['normal', 'percent'],
        yAxisName: ['内存（MB)', 'cpu']
      }
    },
    computed: {
    fullName () {
      return this.chartData
    }
  },


  }

</script>

<style>


</style>
