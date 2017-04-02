<template>
  <div id="index">
    <div class="columns">
      <div class="column is-10-mobile is-offset-1-mobile is-8-tablet is-offset-2-tablet info-container">
        <div class="box info-box index-box">
          <table class="table is-striped">
            <thead>
              <tr>
                <th>项目名</th>
                <th>值</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>主机</td>
                <td>{{ this.info.host }}</td>
              </tr>
              <tr>
                <td>端口</td>
                <td>{{ this.info.port }}</td>
              </tr>
              <tr>
                <td>版本</td>
                <td>{{ this.info.version }}</td>
              </tr>
              <tr>
                <td>运行时间</td>
                <td>{{ this.run_time }}</td>
              </tr>
              <tr>
                <td>主机上传速率</td>
                <td>{{ this.speed_up }}</td>
              </tr>
              <tr>
                <td>主机下载速率</td>
                <td>{{ this.speed_down }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import prettysize from 'prettysize'
export default {
  data () {
    return {
      info: {},
      speed: null,
      speed_last: null,
      get_speed_time: null
    }
  },
  created () {
    this.$http.get('config')
    .then(response => response.json())
    .then((json) => {
      this.info = json
    })
    this.get_speed()
    setInterval(this.get_speed, 1000)
    setInterval(this.inc_time, 1000)
  },
  methods: {
    get_speed () {
      const d = new Date()
      this.get_speed_time = d.getTime()
      this.$http.get('speed')
      .then(response => response.json())
      .then((json) => {
        const temp = new Date()
        this.get_speed_time = temp.getTime() - this.get_speed_time
        this.speed_last = this.speed
        this.speed = json
      })
    },
    inc_time () {
      this.info.uptime = parseInt(this.info.uptime) + 1
    }
  },
  computed: {
    speed_up () {
      if (this.speed && this.speed_last) {
        const up = prettysize((parseInt(this.speed.up) - parseInt(this.speed_last.up)) / this.get_speed_time * 1000)
        return `${up}/s`
      } else {
        return ''
      }
    },
    speed_down () {
      if (this.speed && this.speed_last) {
        const down = prettysize((parseInt(this.speed.down) - parseInt(this.speed_last.down)) / this.get_speed_time * 1000)
        return `${down}/s`
      } else {
        return ''
      }
    },
    run_time () {
      if (this.info) {
        let s = parseInt(this.info.uptime)
        let min = parseInt(s / 60)
        s = s % 60
        let hour = parseInt(min / 60)
        min = min % 60
        /* eslint no-unused-vars: 0 */
        const day = parseInt(hour / 24)
        hour = hour % 24
        return `${day} 天 ${hour} 小时 ${min} 分钟 ${s} 秒`
      } else {
        return ''
      }
    }
  }
}
</script>

<style>
#index {
  padding: 24px 0;
}
.index-box {
  padding: 12px 12px;
}
</style>
