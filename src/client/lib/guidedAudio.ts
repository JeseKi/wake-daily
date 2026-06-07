export interface GuidedAudio {
  day: number
  label: string
  url?: string
}

export const GUIDED_AUDIO_BY_DAY: Record<number, GuidedAudio> = {
  1: {
    day: 1,
    label: '第一天：身体扫描·扎根当下',
    url: 'https://present-files-1317479375.cos.ap-guangzhou.myqcloud.com/present-files-1317479375/1/object_15772eed99ae4acc9332e96bb335f20f_%E7%AC%AC%E4%B8%80%E5%A4%A9%EF%BC%9A%E8%BA%AB%E4%BD%93%E6%89%AB%E6%8F%8F%C2%B7%E6%89%8E%E6%A0%B9%E5%BD%93%E4%B8%8B.mp3',
  },
  2: {
    day: 2,
    label: '第二天：肌肉释放·溶解紧绷',
    url: 'https://present-files-1317479375.cos.ap-guangzhou.myqcloud.com/present-files-1317479375/1/object_53028427ddc44c5ab375dbb26b018743_%E7%AC%AC%E4%BA%8C%E5%A4%A9%EF%BC%9A%E8%82%8C%E8%82%89%E9%87%8A%E6%94%BE%C2%B7%E6%BA%B6%E8%A7%A3%E7%B4%A7%E7%BB%B7.mp3',
  },
  3: {
    day: 3,
    label: '第三天：皮肤知觉·呼吸如水',
    url: 'https://present-files-1317479375.cos.ap-guangzhou.myqcloud.com/present-files-1317479375/1/object_600074bffd814a8a8d97ac29913e5a83_%E7%AC%AC%E4%B8%89%E5%A4%A9%EF%BC%9A%E7%9A%AE%E8%82%A4%E7%9F%A5%E8%A7%89%C2%B7%E5%91%BC%E5%90%B8%E5%A6%82%E6%B0%B4.mp3',
  },
  4: { day: 4, label: '第四天引导语音准备中' },
  5: { day: 5, label: '第五天引导语音准备中' },
  6: { day: 6, label: '第六天引导语音准备中' },
  7: { day: 7, label: '第七天引导语音准备中' },
}

export const GUIDED_AUDIO_LIST = Object.values(GUIDED_AUDIO_BY_DAY).sort(
  (first, second) => first.day - second.day,
)
