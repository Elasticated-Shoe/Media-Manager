using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.ResponseCompression;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.IO.Compression;
using System.Linq;
using System.Threading.Tasks;

namespace Media_Manager.Configuration
{
    public static class CompressionConfig
    {
        public static IServiceCollection ConfigureCompression(this IServiceCollection services, AppSettings _AppSettings)
        {
            if (_AppSettings.Compression.Type == "GZIP")
            {
                services.Configure<GzipCompressionProviderOptions>(options => options.Level = (CompressionLevel)_AppSettings.Compression.Level);
                services.AddResponseCompression(options =>
                {
                    options.Providers.Add<GzipCompressionProvider>();
                });
            }
            else if (_AppSettings.Compression.Type == "BROTLI")
            {
                services.AddResponseCompression(options =>
                {
                    options.Providers.Add<BrotliCompressionProvider>();
                });
            }
            else if (_AppSettings.Compression.Type != "DISABLED")
                throw new Exception($"Config Option For {_AppSettings.Compression.Type} Not Recognised");

            return services;
        }

        public static void UseCompression(this IApplicationBuilder app, AppSettings _AppSettings)
        {
            if (_AppSettings.Compression.Type != "DISABLED")
                app.UseResponseCompression();
        }
    }
}
