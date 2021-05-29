const HISTORY_SIZE = 5

export default class Progress {
    public sizeBytes: number = 0
    public downloadedBytes: number = 0
    public ratio: number = 0
    public history: ProgressHistoryEntry[] = []
    public rate: number = 0
    public unit: string = ''

    get percentString() {
        if (this.ratio < 0 || isNaN(this.ratio)) {
            return '0%';
        }
        else {
            return `${Math.round(this.ratio * 100)}%`;
        }
    }

    get rateString() {
        if (this.rate === 0) {
            return '';
        }
        else {
            return `${this.rate.toFixed(2)} ${this.unit}`;
        }
    }

    updateRate(downloadedBytes: number) {
        this.history.push({time: Date.now(), downloadedBytes: downloadedBytes});
        if (this.history.length > HISTORY_SIZE) {
            this.history.shift();
        }
        let delta = this.history[this.history.length - 1].downloadedBytes - this.history[0].downloadedBytes;
        let duration = this.history[this.history.length - 1].time - this.history[0].time;
        this.rate = delta / (duration / 1000);
        this.unit = 'B/s';
        ['KB/s', 'MB/s'].forEach((unit) => {
            if (this.rate / 1000 > 1) {
                this.unit = unit;
                this.rate = this.rate / 1000;
            }
        })
    }

    update(sizeBytes: number, downloadedBytes: number) {
        this.sizeBytes = sizeBytes;
        this.downloadedBytes = downloadedBytes;
        this.ratio = downloadedBytes / sizeBytes;
        this.updateRate(downloadedBytes);
    }
}

interface ProgressHistoryEntry {
    time: number,
    downloadedBytes: number
}