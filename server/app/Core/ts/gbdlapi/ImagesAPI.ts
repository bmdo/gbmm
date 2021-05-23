import {ResponseData} from "./API";

export interface ImageResponseData extends ResponseData {
    /** Database ID of the image. */
    id: number
    /** URL to the icon version of the image. */
    icon_url: string
    /** URL to the medium size of the image. */
    medium_url: string
    /** URL to the original image. */
    original_url: string
    /** URL to the screenshot version of the image. */
    screen_url: string
    /** URL to the large screenshot version of the image. */
    screen_large_url: string
    /** URL to the small version of the image. */
    small_url: string
    /** URL to the super sized version of the image. */
    super_url: string
    /** URL to the thumb-sized version of the image. */
    thumb_url: string
    /** URL to the tiny version of the image. */
    tiny_url: string
    /** Name of image tag for filtering images. */
    image_tags: string
}