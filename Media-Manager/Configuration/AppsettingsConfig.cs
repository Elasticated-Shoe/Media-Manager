using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Media_Manager.Configuration
{
    public static class AppsettingsConfig
    {
        public static IHostBuilder ConfigureSettings(this IHostBuilder hostBuilder)
        {
            hostBuilder.ConfigureAppConfiguration(config => config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: false));

            hostBuilder.ConfigureServices((hostContext, services) =>
            {
                services.Configure<AppSettings>(hostContext.Configuration);
            });

            return hostBuilder;
        }
    }
    public class AppSettings
    {
        public int[] Ports { get; set; }
        public Compression Compression { get; set; }
        public Cors Cors { get; set; }
        public string ConnectionString { get; set; }
        public bool InbuiltStaticServe { get; set; }
        public string MediaUrl { get; set; }
        public string MediaDir { get; set; }
    }
    public class Cors
    {
        public string Policy { get; set; }
        public string[]? Allowed { get; set; }
    }
    public class Compression
    {
        public string Type { get; set; }
        public int? Level { get; set; }
    }
}
