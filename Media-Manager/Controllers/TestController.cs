using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Media_Manager.Configuration;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace Media_Manager.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class TestController : ControllerBase
    {
        private MediaDbContext _DBManager;
        private AppSettings _AppSettings { get; }
        public TestController(MediaDbContext DBManager, IOptionsMonitor<AppSettings> AppSettings)
        {
            _DBManager = DBManager;
            _AppSettings = AppSettings.CurrentValue;
        }
        [Route("Settings")]
        [HttpGet]
        public ActionResult GetSettings()
        {
            return Ok(_AppSettings);
        }
        [Route("Database")]
        [HttpGet]
        public ActionResult GetDatabase()
        {
            return Ok(_DBManager.PeopleMetadata);
        }
    }
}
