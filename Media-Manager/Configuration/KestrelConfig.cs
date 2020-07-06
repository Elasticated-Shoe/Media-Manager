using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.FileProviders;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading.Tasks;

namespace Media_Manager.Configuration
{
    public static class KestrelConfig
    {
        public static IWebHostBuilder ConfigureKestrel(this IWebHostBuilder webBuilder)
        {
            webBuilder.UseKestrel();
            webBuilder.ConfigureKestrel((context, options) =>
            {
                var ports = new List<int>();
                context.Configuration.GetSection("Ports").Bind(ports);

                IPAddress ip = IPAddress.Parse("0.0.0.0");
                foreach(int port in ports)
                    options.Listen(ip, port);
            });

            return webBuilder;
        }
        public static void UseKestrel(this IApplicationBuilder app, AppSettings _AppSettings)
        {
            if(_AppSettings.InbuiltStaticServe)
                app.UseStaticFiles(new StaticFileOptions
                {
                    FileProvider = new PhysicalFileProvider(_AppSettings.MediaDir),
                    RequestPath = _AppSettings.MediaUrl
                });
        }
    }
}
