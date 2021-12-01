<template>
  <v-suggest
    :data="example"
    show-field="name"
    v-model="myValue"
  ></v-suggest>
</template>

<script>
import { Suggest } from 'v-suggest'

export default {
  data () {
    return {
      myValue: '',
      example: [
        { id: 1, name: 'Chicago Bulls', desc: '芝加哥公牛' },
        { id: 2, name: 'Cleveland Cavaliers', desc: '克里夫兰骑士' }
      ]
    }
  },
  components: {
    'v-suggest': Suggest
  }
}
</script>
