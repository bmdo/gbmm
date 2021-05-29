import {MultipleResponseData, MultipleResponseMetadata, ResponseData} from "./gbdlapi/API";
import Definitions from "./Definitions";

export default class ResultList<T> extends Array<T> {
    public metadata: MultipleResponseMetadata

    public constructor(t?: {new(r: ResponseData, d?: Definitions): T}, data?: MultipleResponseData<any>, definitions?: Definitions) {
        super();
        for (let item of data?.results ?? []) {
            this.push(new t(item, definitions));
        }
        this.metadata = {
            limit: data?.metadata?.limit,
            offset: data?.metadata?.offset,
            current_page: data?.metadata?.current_page,
            total_pages: data?.metadata?.total_pages,
            total_results: data?.metadata?.total_results
        }
    }
}