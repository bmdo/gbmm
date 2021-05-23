const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
    mode: 'development',
    entry: './server/app/areas/index.ts',
    devtool: 'inline-source-map',
    module: {
        rules: [
            // TypeScript
            {
                test: /\.tsx?$/,
                loader: 'ts-loader',
                exclude: /node_modules/,
                options: {
                    appendTsSuffixTo: [/\.vue$/]
                }
            },
            // Vue
            {
                test: /\.vue$/,
                use: [
                    'vue-loader'
                ],
                exclude: /node_modules/
            },
            // SASS
            {
                test: /\.s[ac]ss$/,
                use: [
                    'vue-style-loader',
                    'style-loader',
                    'css-loader',
                    {
                        loader: 'sass-loader',
                        options: {
                            sassOptions: {
                                // Needed this to get Vue single file component SASS to work
                                indentedSyntax: true
                            },
                        },
                    },
                ],
                exclude: /node_modules/,
            },
            // SVG
            {
                test: /\.svg$/,
                type: 'asset/resource'
            }
        ],
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    resolve: {
        extensions: ['.tsx', '.ts', '.js'],
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        }
    },
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, './server/app/static'),
        assetModuleFilename: 'svg/[hash][ext][query]'
    }
}